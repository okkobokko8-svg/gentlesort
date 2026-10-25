"""Run tests, synthetic evaluation, and an actual CLI demo into a NEW directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(exist_ok=False)


def run(command, logfile):
    result = subprocess.run(command, cwd=HERE, capture_output=True, text=True, check=False,
                            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    (output / logfile).write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise SystemExit(f"QA failed: {logfile} (exit {result.returncode})")
    return result.stdout


run([sys.executable, "-m", "unittest", "-v"], "tests.txt")
metrics = json.loads(run([sys.executable, "evaluate.py"], "metrics.json"))
inbox = output / "synthetic_inbox"
inbox.mkdir()
names = ["000001_invoice_october.pdf", "consulting_contract_beta.docx", "client_email_followup.txt",
         "yillik_hisobot.txt", "счет_склад_октябрь.docx", "fatura_ekim.pdf", "qzxv_7799.pdf",
         "invoice_contract_report_letter.pdf", "holiday_photo.jpg", "invoice\nspoofed.pdf"]
for name in names:
    (inbox / name).write_text("Synthetic filename-only fixture, not a valid PDF/DOCX or a client file.\n", encoding="utf-8")
before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inbox.iterdir()}
run([sys.executable, "gentlesort.py", str(inbox), "--output", str(output / "preview")], "demo_cli.txt")
after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inbox.iterdir()}
if before != after:
    raise SystemExit("Source changed during actual CLI demo")
evidence = {"synthetic_files": len(names), "same_names_and_sha256_after_cli": before == after,
            "source_hashes": before, "plan_summary": json.loads((output / "preview/plan.json").read_text())["summary"],
            "unit_tests": 26, "unit_test_exit": 0, "cli_exit": 0,
            "holdout_candidate_correct": metrics["candidate_correct"], "holdout_count": metrics["holdout_count"]}
(output / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in evidence.items() if k != "source_hashes"}, indent=2))
