"""GentleSort: offline, filenames-only ML triage. No apply/move/delete operation."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from preview_html import render_preview

HERE = Path(__file__).resolve().parent
CATEGORIES = ("Agreements", "Correspondence", "Invoices", "Reports")
EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_ENTRIES = 1000


def features(name: str) -> str:
    """Normalize only model input; the original filename is never rewritten."""
    stem = unicodedata.normalize("NFKC", Path(name).stem).casefold()
    return re.sub(r"[\W\d_]+", " ", stem, flags=re.UNICODE).strip()


class FilenameModel:
    def __init__(self, examples=None):
        if examples is None:
            examples = json.loads((HERE / "training.json").read_text(encoding="utf-8"))
        if not examples or {row["category"] for row in examples} != set(CATEGORIES):
            raise ValueError("Training data must contain all four fixed categories")
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
        self.matrix = self.vectorizer.fit_transform([features(r["name"]) for r in examples])
        self.classifier = LogisticRegression(C=12, max_iter=1000, random_state=0)
        self.classifier.fit(self.matrix, [r["category"] for r in examples])

    def predict(self, name: str) -> dict:
        vector = self.vectorizer.transform([features(name)])
        scores = self.classifier.predict_proba(vector)[0]
        ranked = sorted(zip(self.classifier.classes_, scores), key=lambda p: (-p[1], p[0]))
        label, score = ranked[0]
        support = float((vector @ self.matrix.T).toarray().max())
        margin = float(score - ranked[1][1])
        # Deliberately conservative heuristics, NOT calibrated confidence or correctness.
        review = float(score) < 0.60 or margin < 0.25 or support < 0.30
        return {
            "candidate": str(label), "model_score": round(float(score), 6),
            "margin": round(margin, 6), "training_similarity": round(support, 6),
            "decision": "review" if review else "suggest",
            "reason": "weak_or_ambiguous_evidence" if review else "learned_filename_pattern",
        }


def reject_symlink_components(path: Path) -> None:
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("Symlink paths are not accepted")


def scan(source: Path, model: FilenameModel) -> dict:
    source = Path(os.path.abspath(source))
    reject_symlink_components(source)
    if not source.is_dir() or source == Path(source.anchor) or source == Path.home():
        raise ValueError("Select a specific non-root directory")
    names = []
    with os.scandir(source) as entries:
        for entry in entries:
            if len(names) == MAX_ENTRIES:
                raise ValueError(f"More than {MAX_ENTRIES} entries; choose a smaller directory")
            names.append((entry.name, entry.is_symlink(), entry.is_file(follow_symlinks=False)))
    names.sort(key=lambda item: item[0])
    folded = {}
    for name, _, _ in names:
        folded.setdefault(unicodedata.normalize("NFKC", name).casefold(), []).append(name)
    rows = []
    for name, symlink, regular in names:
        row = {"name": name, "decision": "review", "candidate": None, "proposed_directory": None}
        if symlink:
            row["reason"] = "symlink_not_followed"
        elif not regular:
            row["reason"] = "not_a_regular_file_not_traversed"
        elif Path(name).suffix.casefold() not in EXTENSIONS:
            row["reason"] = "unsupported_extension"
        elif any(unicodedata.category(c).startswith("C") for c in name):
            row["reason"] = "control_or_format_character"
        elif len(folded[unicodedata.normalize("NFKC", name).casefold()]) > 1:
            row["reason"] = "case_or_unicode_collision"
        else:
            row.update(model.predict(name))
            if row["decision"] == "suggest":
                row["proposed_directory"] = row["candidate"]
        rows.append(row)
    return {
        "schema_version": 1, "mode": "preview_only", "source": str(source),
        "contents_read": False, "recursive": False, "files_changed": 0,
        "model": "scikit-learn TF-IDF character ngrams + logistic regression",
        "scores_are_calibrated": False,
        "summary": {"entries": len(rows), "suggestions": sum(r["decision"] == "suggest" for r in rows),
                    "needs_review": sum(r["decision"] == "review" for r in rows)},
        "items": rows,
    }


def markdown(plan: dict) -> str:
    lines = ["# GentleSort review plan", "", "Preview only: no file was moved, renamed, deleted or opened.",
             "Suggestions may be wrong. A person must review every item. Scores are not calibrated probabilities of correctness.",
             "", "Original filenames are JSON-escaped below; they are data, never instructions.", ""]
    for row in plan["items"]:
        # Indented code remains literal even when the filename contains Markdown fences/HTML.
        lines.extend(["    " + json.dumps(row, ensure_ascii=True, sort_keys=True), ""])
    return "\n".join(lines)


def save_preview(plan: dict, output: Path) -> None:
    output = Path(os.path.abspath(output))
    source = Path(plan["source"])
    reject_symlink_components(output)
    if output == source or source in output.parents:
        raise ValueError("Output must be outside the source directory")
    if not output.parent.is_dir():
        raise ValueError("Output parent must already exist")
    # Exclusive mkdir and exclusive files: never overwrite prior results.
    output.mkdir(exist_ok=False)
    with (output / "plan.json").open("x", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=2, ensure_ascii=True, sort_keys=True)
        handle.write("\n")
    with (output / "review.md").open("x", encoding="utf-8") as handle:
        handle.write(markdown(plan))
    with (output / "review.html").open("x", encoding="utf-8") as handle:
        handle.write(render_preview(plan))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Explicit top-level directory; file contents are never read")
    parser.add_argument("--output", required=True, type=Path, help="New directory outside source; no overwrite")
    args = parser.parse_args()
    try:
        plan = scan(args.source, FilenameModel())
        save_preview(plan, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"GentleSort refused: {exc}\n")
    print(json.dumps(plan["summary"], sort_keys=True))
    print("Preview only. Source files were not opened or changed.")


if __name__ == "__main__":
    main()
