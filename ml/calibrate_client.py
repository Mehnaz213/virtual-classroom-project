"""
Generate calibration offsets from recorded sessions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Aggregate calibration recordings into client offsets.")
    parser.add_argument("--recordings", type=Path, required=True, help="JSONL with calibration frames")
    parser.add_argument("--out", type=Path, required=True, help="Output calibration JSON")
    args = parser.parse_args()

    yaw_offsets = []
    pitch_offsets = []
    for line in args.recordings.read_text().splitlines():
        row = json.loads(line)
        yaw_offsets.append(row.get("gaze_yaw", 0.0) - row.get("target_yaw", 0.0))
        pitch_offsets.append(row.get("gaze_pitch", 0.0) - row.get("target_pitch", 0.0))

    calibration = {
        "yaw_offset": float(sum(yaw_offsets) / max(len(yaw_offsets), 1)),
        "pitch_offset": float(sum(pitch_offsets) / max(len(pitch_offsets), 1)),
    }
    args.out.write_text(json.dumps(calibration, indent=2))
    print(f"[calibrate] wrote {args.out}")


if __name__ == "__main__":
    main()

"""
Generate per-device calibration offsets from recorded samples.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute calibration offsets.")
    parser.add_argument("--recordings", type=Path, required=True, help="JSON lines with gaze samples.")
    parser.add_argument("--output", type=Path, default=Path("calibration.json"))
    args = parser.parse_args()

    yaw = []
    pitch = []
    with args.recordings.open() as fp:
        for line in fp:
            payload = json.loads(line)
            yaw.append(payload["gaze"][0])
            pitch.append(payload["gaze"][1])

    calibration = {"yawOffset": mean(yaw), "pitchOffset": mean(pitch)}
    args.output.write_text(json.dumps(calibration, indent=2), encoding="utf-8")
    print(f"Calibration saved to {args.output}")


if __name__ == "__main__":
    main()


