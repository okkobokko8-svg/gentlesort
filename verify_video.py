"""Check encoded demo metadata, decode, and six scene samples against rendered source."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageChops, ImageStat

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("render_directory", type=Path)
args = parser.parse_args()
render = args.render_directory.resolve()
video = render / "GentleSort_Demo_20261020.mp4"
manifest = json.loads((render / "manifest.json").read_text(encoding="utf-8"))
qa = render / "video_qa"
qa.mkdir(exist_ok=False)
probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)], text=True))
streams = probe["streams"]
assert len(streams) == 1 and streams[0]["codec_type"] == "video", "Unexpected audio/extra stream"
stream = streams[0]
assert (stream["width"], stream["height"]) == (1600, 900)
assert stream["r_frame_rate"] == "12/1" and int(stream["nb_frames"]) == 876
assert abs(float(probe["format"]["duration"]) - 73) < 0.01
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(video), "-f", "null", "-"], check=True)
elapsed = 0
checks = []
for number, scene in enumerate(manifest["scenes"]):
    center = elapsed + scene["seconds"] / 2
    frame = qa / f"encoded_scene_{number:02d}.png"
    subprocess.run(["ffmpeg", "-nostdin", "-n", "-v", "error", "-ss", str(center), "-i", str(video),
                    "-frames:v", "1", str(frame)], check=True)
    with Image.open(render / scene["file"]) as expected, Image.open(frame) as actual:
        diff = ImageStat.Stat(ImageChops.difference(expected.convert("RGB"), actual.convert("RGB")))
        mae = sum(diff.mean) / 3
    assert mae < 5, f"Encoded scene does not match source: {number}: {mae}"
    checks.append({"scene": number, "sample_seconds": center, "mean_absolute_pixel_error": round(mae, 6)})
    elapsed += scene["seconds"]
result = {"status": "PASS", "codec": stream["codec_name"], "width": 1600, "height": 900,
          "fps": 12, "frames": int(stream["nb_frames"]), "duration_seconds": float(probe["format"]["duration"]),
          "audio": False, "full_decode_exit": 0, "scene_samples": checks,
          "video_sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
          "limitations": "Metadata/decode/sample-match checks, not proof of contest eligibility or real-client usefulness. Visual source-scene review is separate."}
(qa / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
