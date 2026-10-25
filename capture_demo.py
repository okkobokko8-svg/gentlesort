"""Capture real CLI execution on eight original synthetic filenames. No client files."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True, help="New capture directory, never overwritten")
args = parser.parse_args()
capture = args.output.resolve()
capture.mkdir(exist_ok=False)
inbox = capture / "inbox"
inbox.mkdir()
names = ["000001_invoice_october.pdf", "consulting_contract_beta.docx", "client_email_followup.txt",
         "yillik_hisobot.txt", "fatura_ekim.pdf", "qzxv_7799.pdf",
         "invoice_contract_report_letter.pdf", "holiday_photo.jpg"]
for name in names:
    (inbox / name).write_text("Original synthetic filename fixture; not a valid PDF/Word/image document.\n", encoding="utf-8")


def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inbox.iterdir())}


before = hashes()
events = []


def command_event(title, argv):
    started = perf_counter()
    result = subprocess.run(argv, cwd=HERE, capture_output=True, text=True, check=False,
                            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    event = {"title": title, "kind": "subprocess", "argv": argv,
             "stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode,
             "actual_seconds": round(perf_counter() - started, 6)}
    events.append(event)
    if result.returncode:
        raise SystemExit(f"Demo failed: {title}: {result.stderr}")


relative_inbox = os.path.relpath(inbox, HERE)
relative_preview = os.path.relpath(capture / "preview", HERE)
command_event("Actual classifier execution", [sys.executable, "gentlesort.py", relative_inbox,
                                            "--output", relative_preview])
plan = json.loads((capture / "preview/plan.json").read_text(encoding="utf-8"))
table = ["DECISION   PROPOSED FOLDER   ORIGINAL FILENAME", "-" * 82]
for item in plan["items"]:
    table.append(f'{item["decision"]:<10} {(item["proposed_directory"] or "(none)"):<17} {item["name"]}')
table.extend(["", f'Suggestions: {plan["summary"]["suggestions"]} | Human review: {plan["summary"]["needs_review"]}',
              "All suggestions still need human review; a score is not a correctness guarantee."])
events.append({"title": "Inspector reads the actual generated plan.json", "kind": "verified_inspection",
               "stdout": "\n".join(table) + "\n", "stderr": "", "exit_code": 0,
               "source_artifact": "preview/plan.json"})
command_event("Actual regression tests", [sys.executable, "-m", "unittest", "-v"])
after = hashes()
if before != after:
    raise SystemExit("Source hashes or names changed")
hash_lines = ["VERIFIER: compare fixture filenames and SHA-256 before/after.",
              "Names preserved: 8 / 8", "Content hashes preserved: 8 / 8", "",
              "Classifier: names only; no file-content reads or move/delete/apply operation.",
              "Independent verifier: reads synthetic bytes to compute SHA-256.", "",
              "No client content, external model, API request or public submission."]
events.append({"title": "Actual fixture integrity verification", "kind": "verified_inspection",
               "stdout": "\n".join(hash_lines) + "\n", "stderr": "", "exit_code": 0})
result = {"schema": 1, "description": "Actual subprocess stdout/stderr and verified inspection; not a desktop screen recording",
          "python": platform.python_version(), "synthetic_file_count": len(names),
          "source_before": before, "source_after": after, "same_names_and_hashes": before == after,
          "events": events, "presentation_note": "Video replay extends pauses for readability; displayed timing is not execution latency."}
(capture / "execution.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"events": len(events), "same_names_and_hashes": before == after,
                  "plan_summary": plan["summary"], "capture": str(capture)}, indent=2))
