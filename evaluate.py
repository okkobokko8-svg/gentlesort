"""Print reproducible synthetic holdout results. This is not a real-world benchmark."""
import importlib.metadata
import json
from pathlib import Path
import platform
from time import perf_counter

from gentlesort import FilenameModel

start = perf_counter()
model = FilenameModel()
training_seconds = perf_counter() - start
holdout = json.loads((Path(__file__).parent / "holdout.json").read_text(encoding="utf-8"))
results = []
start = perf_counter()
for row in holdout:
    prediction = model.predict(row["name"])
    results.append({"name": row["name"], "expected": row["category"], **prediction})
inference_seconds = perf_counter() - start
suggested = [r for r in results if r["decision"] == "suggest"]
print(json.dumps({
    "dataset": "Original synthetic filenames; 48 training, 16 holdout; no real customer files",
    "limitations": "Tiny hand-written related-language examples; no generalization or time-savings claim. Thresholds manually selected, not calibrated. Holdout is inspectable and not blind external validation.",
    "python": platform.python_version(),
    "versions": {n: importlib.metadata.version(n) for n in ["scikit-learn", "numpy", "scipy", "joblib", "threadpoolctl"]},
    "training_seconds_this_run": round(training_seconds, 6),
    "holdout_inference_seconds_this_run": round(inference_seconds, 6),
    "holdout_count": len(results), "candidate_correct": sum(r["candidate"] == r["expected"] for r in results),
    "suggested_count": len(suggested), "suggested_correct": sum(r["candidate"] == r["expected"] for r in suggested),
    "review_count": len(results) - len(suggested),
    "majority_class_baseline_correct": 4,
    "unknown_probe": model.predict("qzxv_7799.pdf"),
    "ambiguous_probe": model.predict("invoice_contract_report_letter.pdf"),
    "items": results,
}, ensure_ascii=False, indent=2))
