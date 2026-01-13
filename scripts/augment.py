"""
Augmentation and synthesis pipeline for Focus Mate gaze samples.

Reads the unified metadata.jsonl produced by `scripts/data_ingest.py`,
applies photometric/pose augmentations, and writes augmented frames +
metadata back to disk.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None


def _load_metadata(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            yield json.loads(line)


def _save_metadata(records, output_path: Path):
    with output_path.open("w", encoding="utf-8") as handle:
        for row in records:
            handle.write(json.dumps(row) + "\n")


def random_brightness(image, factor=None):
    factor = factor or random.uniform(0.5, 1.5)
    return np.clip(image * factor, 0, 255).astype(np.uint8)


def add_occlusion(image, size=0.2):
    h, w = image.shape[:2]
    occ_w, occ_h = int(w * size), int(h * size)
    x = random.randint(0, w - occ_w)
    y = random.randint(0, h - occ_h)
    image[y : y + occ_h, x : x + occ_w] = 0
    return image


def gaussian_noise(image, sigma=10):
    noise = np.random.normal(0, sigma, image.shape).astype(np.float32)
    return np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def process(
    metadata_path: Path,
    output_dir: Path,
    augmentations=("brightness", "occlusion", "noise"),
    copies: int = 1,
):
    if cv2 is None:
        raise RuntimeError("OpenCV not available; install opencv-python to use augmentations.")

    output_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    augmented_records = []
    for record in _load_metadata(metadata_path):
        frame = cv2.imread(record["frame_path"])
        if frame is None:
            continue

        for idx in range(copies):
            aug = frame.copy()
            label = record["label"]
            if "brightness" in augmentations:
                aug = random_brightness(aug)
            if "occlusion" in augmentations and random.random() < 0.5:
                aug = add_occlusion(aug)
                label = "distracted_by_multi_face"
            if "noise" in augmentations:
                aug = gaussian_noise(aug)

            out_path = frames_dir / f"{Path(record['frame_path']).stem}_aug{idx}.jpg"
            cv2.imwrite(str(out_path), aug)

            new_record = {
                **record,
                "frame_path": str(out_path.resolve()),
                "label": label,
                "meta": {**record.get("meta", {}), "augmented": True},
            }
            augmented_records.append(new_record)

    _save_metadata(augmented_records, output_dir / "metadata.jsonl")
    print(f"[augment] wrote {len(augmented_records)} samples to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Augment unified dataset samples")
    parser.add_argument("metadata", type=Path, help="Path to metadata.jsonl")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument("--copies", type=int, default=1, help="Augmented samples per frame")
    parser.add_argument(
        "--augmentations",
        nargs="+",
        default=["brightness", "occlusion", "noise"],
        help="Augmentations to apply",
    )
    args = parser.parse_args()
    process(args.metadata, args.out, args.augmentations, args.copies)


if __name__ == "__main__":
    main()


