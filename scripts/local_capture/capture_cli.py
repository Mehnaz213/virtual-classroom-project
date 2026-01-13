"""
Simple calibration capture utility.

Prompts the user to look at specific directions and saves frames +
metadata for later ingestion via data_ingest.py.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

import cv2

PROMPTS = [
    ("focused", "Look at the center of the screen"),
    ("looking_left", "Turn your eyes/head left"),
    ("looking_right", "Look right"),
    ("looking_up", "Look up"),
    ("looking_down", "Look down"),
    ("partial_engaged", "Glance away briefly"),
    ("sleepy", "Blink slowly / simulate drowsiness"),
    ("no_face", "Step out of frame"),
]


def capture_session(output_dir: Path, prompts: List[tuple[str, str]], frames_per_prompt: int = 30):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Unable to open webcam")

    session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    session_dir = output_dir / session_id
    frames_dir = session_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    for label, instruction in prompts:
        print(f"[{label}] {instruction}")
        input(" Press Enter to start recording frames...")
        for frame_idx in range(frames_per_prompt):
            ret, frame = cap.read()
            if not ret:
                continue
            frame_path = frames_dir / f"{label}_{frame_idx:04d}.jpg"
            cv2.imwrite(str(frame_path), frame)

        metadata = {
            "label": label,
            "instruction": instruction,
            "timestamp": datetime.utcnow().isoformat(),
            "frames_per_prompt": frames_per_prompt,
        }
        (session_dir / f"{label}_metadata.json").write_text(json.dumps(metadata, indent=2))

    cap.release()
    print(f"[capture] session saved under {session_dir}")


def main():
    parser = argparse.ArgumentParser(description="Capture labeled calibration frames")
    parser.add_argument("--out", type=Path, default=Path("data/raw/local_calibration"))
    parser.add_argument("--frames", type=int, default=30, help="Frames per prompt")
    args = parser.parse_args()
    capture_session(args.out, PROMPTS, frames_per_prompt=args.frames)


if __name__ == "__main__":
    main()


