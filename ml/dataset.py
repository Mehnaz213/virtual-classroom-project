"""
Unified dataset loader for the training pipeline.
Reads metadata.jsonl entries produced by scripts/data_ingest.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import numpy as np

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None


@dataclass
class Sample:
    image: np.ndarray
    gaze_yaw: float
    gaze_pitch: float
    head_yaw: float
    head_pitch: float
    eyes_open_prob: float
    label: str
    confidence: float


def load_metadata(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def load_samples(metadata_path: Path) -> List[Sample]:
    """
    Load samples from metadata.jsonl file.
    Resolves frame_path relative to metadata file location.
    """
    entries = load_metadata(metadata_path)
    samples: List[Sample] = []
    base_dir = metadata_path.parent
    
    for row in entries:
        frame_path = row.get("frame_path", "")
        image_path = base_dir / frame_path if not Path(frame_path).is_absolute() else Path(frame_path)
        
        if cv2 is None:
            # Create dummy image for testing without cv2
            img = np.zeros((120, 160, 3), dtype=np.uint8)
        elif not image_path.exists():
            print(f"[Focus Mate Dataset] Warning: Image not found: {image_path}")
            continue
        else:
            img = cv2.imread(str(image_path))
            if img is None:
                print(f"[Focus Mate Dataset] Warning: Failed to load: {image_path}")
                continue
        
        samples.append(
            Sample(
                image=img,
                gaze_yaw=float(row.get("gaze_yaw", 0.0)),
                gaze_pitch=float(row.get("gaze_pitch", 0.0)),
                head_yaw=float(row.get("head_yaw", 0.0)),
                head_pitch=float(row.get("head_pitch", 0.0)),
                eyes_open_prob=float(row.get("eyes_open_prob", 1.0)),
                label=row.get("label", "unknown"),
                confidence=float(row.get("confidence", 0.5)),
            )
        )
    
    print(f"[Focus Mate Dataset] Loaded {len(samples)} samples from {metadata_path}")
    return samples


def train_val_split(samples: Sequence[Sample], val_ratio: float = 0.1):
    cutoff = int(len(samples) * (1 - val_ratio))
    return samples[:cutoff], samples[cutoff:]


