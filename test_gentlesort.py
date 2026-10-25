import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from html.parser import HTMLParser

from gentlesort import FilenameModel, features, markdown, save_preview, scan
from preview_html import render_preview


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.decisions = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        attrs = dict(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href'))
        if tag == 'article':
            self.decisions.append(attrs.get('data-decision'))

    def handle_data(self, data):
        self.text.append(data)


class GentleSortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = FilenameModel()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "inbox"
        self.source.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, name, body="Original synthetic test content\n"):
        path = self.source / name
        path.write_text(body, encoding="utf-8")
        return path

    def test_clear_invoice(self):
        self.assertEqual(self.model.predict("invoice_new_client.pdf")["candidate"], "Invoices")
        self.assertEqual(self.model.predict("invoice_new_client.pdf")["decision"], "suggest")

    def test_unknown_abstains(self):
        self.assertEqual(self.model.predict("qzxv_7799.pdf")["decision"], "review")

    def test_ambiguous_abstains(self):
        self.assertEqual(self.model.predict("invoice_contract_report_letter.pdf")["decision"], "review")

    def test_original_unicode_name_preserved(self):
        name = "йиллик_ҳисобот_00007.PDF"
        self.make(name)
        self.assertEqual(scan(self.source, self.model)["items"][0]["name"], name)

    def test_leading_zero_name_preserved(self):
        self.make("000001_invoice.pdf")
        self.assertEqual(scan(self.source, self.model)["items"][0]["name"], "000001_invoice.pdf")

    def test_symlinks_are_not_followed(self):
        external = self.root / "outside.txt"
        external.write_text("private test sentinel", encoding="utf-8")
        (self.source / "invoice_link.pdf").symlink_to(external)
        row = scan(self.source, self.model)["items"][0]
        self.assertEqual(row["reason"], "symlink_not_followed")
        self.assertIsNone(row["proposed_directory"])

    def test_symlink_source_rejected(self):
        alias = self.root / "alias"
        alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(ValueError):
            scan(alias, self.model)

    def test_no_recursion(self):
        child = self.source / "subdirectory"
        child.mkdir()
        (child / "invoice_hidden.pdf").write_text("nested", encoding="utf-8")
        plan = scan(self.source, self.model)
        self.assertEqual(plan["summary"]["entries"], 1)
        self.assertEqual(plan["items"][0]["reason"], "not_a_regular_file_not_traversed")

    def test_unsupported_type(self):
        self.make("invoice_script.exe")
        self.assertEqual(scan(self.source, self.model)["items"][0]["reason"], "unsupported_extension")

    def test_control_character(self):
        self.make("invoice\nspoofed.pdf")
        plan = scan(self.source, self.model)
        self.assertEqual(plan["items"][0]["reason"], "control_or_format_character")
        self.assertIn("\\n", markdown(plan))

    def test_case_collision(self):
        self.make("invoice.pdf")
        self.make("INVOICE.PDF")
        self.assertTrue(all(r["reason"] == "case_or_unicode_collision" for r in scan(self.source, self.model)["items"]))

    def test_scan_does_not_open_file_contents(self):
        self.make("invoice.pdf")
        with patch.object(Path, "open", side_effect=AssertionError("File contents opened")):
            self.assertEqual(scan(self.source, self.model)["summary"]["entries"], 1)

    def test_source_hash_and_names_unchanged(self):
        self.make("invoice_0001.pdf", "Synthetic bytes, not a real PDF")
        self.make("contract_0002.docx", "Synthetic bytes, not a real Word file")
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.iterdir()}
        save_preview(scan(self.source, self.model), self.root / "preview")
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.iterdir()}
        self.assertEqual(before, after)

    def test_output_inside_source_refused(self):
        with self.assertRaises(ValueError):
            save_preview(scan(self.source, self.model), self.source / "preview")
        self.assertFalse((self.source / "preview").exists())

    def test_existing_output_never_overwritten(self):
        output = self.root / "preview"
        output.mkdir()
        sentinel = output / "plan.json"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            save_preview(scan(self.source, self.model), output)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_symlink_output_parent_refused(self):
        alias = self.root / "alias"
        alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(ValueError):
            save_preview(scan(self.source, self.model), alias / "preview")

    def test_entry_limit(self):
        for i in range(3):
            self.make(f"invoice_{i}.pdf")
        with patch("gentlesort.MAX_ENTRIES", 2), self.assertRaises(ValueError):
            scan(self.source, self.model)

    def test_root_and_home_refused(self):
        for source in [Path("/"), Path.home()]:
            with self.assertRaises(ValueError):
                scan(source, self.model)

    def test_empty_directory(self):
        self.assertEqual(scan(self.source, self.model)["summary"], {"entries": 0, "suggestions": 0, "needs_review": 0})

    def test_deterministic(self):
        self.make("invoice_a.pdf")
        self.assertEqual(scan(self.source, self.model), scan(self.source, self.model))

    def test_markdown_injection_is_literal(self):
        self.make("```<script>$(touch PWNED)_invoice.pdf")
        result = markdown(scan(self.source, self.model))
        for line in result.splitlines():
            if "<script>" in line:
                self.assertTrue(line.startswith("    {"))
        self.assertFalse((self.root / "PWNED").exists())

    def test_training_and_holdout_distinct(self):
        here = Path(__file__).parent
        train = json.loads((here / "training.json").read_text(encoding="utf-8"))
        hold = json.loads((here / "holdout.json").read_text(encoding="utf-8"))
        self.assertTrue({features(r["name"]) for r in train}.isdisjoint({features(r["name"]) for r in hold}))

    def test_model_really_learns_from_labels(self):
        here = Path(__file__).parent
        train = json.loads((here / "training.json").read_text(encoding="utf-8"))
        mapping = {"Invoices": "Reports", "Reports": "Invoices", "Agreements": "Correspondence", "Correspondence": "Agreements"}
        shuffled = [{"name": r["name"], "category": mapping[r["category"]]} for r in train]
        alternate = FilenameModel(shuffled)
        self.assertEqual(alternate.predict("invoice_new_client.pdf")["candidate"], "Reports")

    def test_html_keeps_all_rows_and_decisions(self):
        for name in ['invoice_0001.pdf', 'qzxv_7799.pdf', 'йиллик_ҳисобот.txt']:
            self.make(name)
        plan = scan(self.source, self.model)
        output = self.root / 'preview'
        save_preview(plan, output)
        parser = ReportParser()
        parser.feed((output / 'review.html').read_text(encoding='utf-8'))
        text = ''.join(parser.text)
        self.assertEqual(len(parser.decisions), len(plan['items']))
        self.assertEqual(parser.decisions.count('suggest'), plan['summary']['suggestions'])
        self.assertEqual(parser.decisions.count('review'), plan['summary']['needs_review'])
        for item in plan['items']:
            self.assertIn(item['name'], text)
        self.assertIn('No folder proposed', text)
        self.assertEqual(json.loads((output / 'plan.json').read_text()), plan)

    def test_html_filename_injection_is_inert(self):
        self.make('<img src=x onerror="alert(1)">_invoice.pdf')
        self.make('invoice\u202ereversed.pdf')
        result = render_preview(scan(self.source, self.model))
        parser = ReportParser()
        parser.feed(result)
        self.assertNotIn('img', parser.tags)
        self.assertNotIn('script', parser.tags)
        self.assertNotIn('iframe', parser.tags)
        self.assertNotIn('form', parser.tags)
        self.assertNotIn('\u202e', result)
        self.assertIn('\\u202e', result)
        self.assertEqual(parser.links, ['plan.json', 'review.md'])

    def test_html_empty_and_tiny_plan_is_complete(self):
        parser = ReportParser()
        parser.feed(render_preview(scan(self.source, self.model)))
        self.assertEqual(parser.decisions, [])
        self.assertEqual(''.join(parser.text).count('No items in this group.'), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
