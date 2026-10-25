"""Render an explicitly labelled replay of captured real output, not a fake recording."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("capture", type=Path)
parser.add_argument("--output", required=True, type=Path, help="New rendering directory")
parser.add_argument("--font", type=Path, default=Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
args = parser.parse_args()
data = json.loads((args.capture / "execution.json").read_text(encoding="utf-8"))
if not data["same_names_and_hashes"] or any(e["exit_code"] for e in data["events"]):
    raise SystemExit("Capture did not pass; no success video will be rendered")
output = args.output.resolve()
output.mkdir(exist_ok=False)
regular = ImageFont.truetype(str(args.font), 21)
small = ImageFont.truetype(str(args.font), 18)
heading = ImageFont.truetype(str(args.font), 34)
events = data["events"]
scan = events[0]
command = shlex.join(scan["argv"])
intro = ["A small offline ML prototype for less manual filing.", "",
         "This video replays actual captured program output.",
         "It is NOT a desktop screen recording or a timed performance benchmark.",
         "Pauses are extended so the output can be read.", "",
         "8 original synthetic filenames | no client documents",
         "scikit-learn TF-IDF + logistic regression | no LLM or paid API",
         "Preview only: no moving, renaming or deleting."]
scan_lines = ["Actual command:", *textwrap.wrap(command, width=104, break_long_words=True), "",
              "Captured stdout:", *scan["stdout"].splitlines(), "", f'Process exit code: {scan["exit_code"]}']
test_output = (events[2]["stdout"] + events[2]["stderr"]).strip().splitlines()
test_lines = ["Actual command: " + shlex.join(events[2]["argv"]), "",
              "Tail of captured output (full transcript in execution.json):", "",
              *test_output[-11:], "", f'Process exit code: {events[2]["exit_code"]}']
final = ["What is ready:", "  Source, original data, 23 tests, preview plan, captured execution.", "",
         "What this does not prove:", "  Real-client accuracy, calibrated scores, real-user time savings.", "",
         "Before any contest entry:", "  Personal review, public repository/demo hosting, final owner approval.", "",
         "Internal prototype only. Not submitted. No prize or payment received."]
scenes = [("GentleSort / honest local inference", intro, 12),
          (scan["title"], scan_lines, 9),
          (events[1]["title"], events[1]["stdout"].splitlines(), 18),
          (events[2]["title"], test_lines, 14),
          (events[3]["title"], events[3]["stdout"].splitlines(), 10),
          ("A review plan, not an automatic file operation", final, 10)]
manifest = []
for number, (title, lines, seconds) in enumerate(scenes):
    wrapped = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, width=108, replace_whitespace=False,
                                     drop_whitespace=False) or [""])
    if len(wrapped) > 22:
        raise SystemExit(f"Scene {number} has too much text: {len(wrapped)}")
    image = Image.new("RGB", (1600, 900), "#0c1522")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((48, 40, 1552, 842), radius=20, fill="#101f30", outline="#315164", width=2)
    draw.text((82, 67), "GentleSort", font=heading, fill="#89e0bd")
    draw.text((490, 79), "ACTUAL OUTPUT REPLAY / SYNTHETIC DATA", font=small, fill="#a2b8c9")
    draw.line((80, 126, 1520, 126), fill="#315164", width=2)
    draw.text((82, 151), title, font=ImageFont.truetype(str(args.font), 25), fill="#eff7fc")
    for index, line in enumerate(wrapped):
        color = "#a4e6cb" if line.strip().startswith(("suggest", "OK", "Names preserved", "Content hashes")) else "#d6e3ee"
        if line.strip().startswith("review"):
            color = "#f7d083"
        draw.text((82, 211 + index * 26), line, font=regular, fill=color)
    draw.text((82, 801), "No desktop recording / no real-time speed claim / source logs included", font=small, fill="#a2b8c9")
    draw.text((1370, 801), f"{number + 1} / 6", font=small, fill="#89e0bd")
    filename = f"scene_{number:02d}.png"
    image.save(output / filename)
    manifest.append({"file": filename, "seconds": seconds, "title": title})
playlist = []
for scene in manifest:
    playlist.extend([f"file '{scene['file']}'", f"duration {scene['seconds']}"])
playlist.append(f"file '{manifest[-1]['file']}'")
(output / "frames.ffconcat").write_text("\n".join(playlist) + "\n", encoding="utf-8")
duration = sum(s["seconds"] for s in manifest)
video = output / "GentleSort_Demo_20261020.mp4"
subprocess.run(["ffmpeg", "-nostdin", "-n", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "1",
                "-i", str(output / "frames.ffconcat"), "-t", str(duration), "-r", "12", "-c:v", "libx264",
                "-preset", "fast", "-tune", "stillimage", "-crf", "12", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)], check=True)
(output / "manifest.json").write_text(json.dumps({"width": 1600, "height": 900, "fps": 12,
          "duration_seconds": duration, "scenes": manifest,
          "note": "Static, honestly labelled output replay. No fabricated terminal output; no desktop recording claim."}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"video": str(video), "duration": duration, "frames_expected": duration * 12}))
