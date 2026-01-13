"""
Adapters that convert raw dataset formats into the unified Focus Mate schema.

Due to licensing restrictions, most public datasets must be downloaded
manually. The adapters below expect the raw archives to be extracted
into `data/raw/<slug>` before running `data_ingest.py`.
"""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import numpy as np

try:
    import cv2
except Exception:  # pragma: no cover - optional dependency during CI
    cv2 = None

from .specs import DatasetSpec

UNIFIED_FIELDS = [
    "frame_path",
    "gaze_yaw",
    "gaze_pitch",
    "head_yaw",
    "head_pitch",
    "eyes_open_prob",
    "label",
    "confidence",
    "meta",
]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_metadata(records: Iterable[dict], output_dir: Path) -> None:
    _ensure_dir(output_dir)
    meta_path = output_dir / "metadata.jsonl"
    with meta_path.open("w", encoding="utf-8") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def adapter_not_implemented(spec: DatasetSpec, *_args, **_kwargs):
    raise NotImplementedError(
        f"Adapter for dataset '{spec.name}' is not implemented yet. "
        "Please contribute parsing logic based on the official annotations."
    )


def local_calibration_adapter(
    spec: DatasetSpec,
    raw_dir: Path,
    output_dir: Path,
    limit: Optional[int] = None,
):
    """
    Convert frames captured via scripts/local_capture into unified format.
    Each capture session stores frames under raw_dir/<session>/frames and
    metadata in metadata.json.
    """

    sessions = list(raw_dir.glob("*"))
    records = []
    for session_dir in sessions:
        meta_path = session_dir / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        label = meta.get("label", "focused")
        frames_dir = session_dir / "frames"
        for idx, frame_path in enumerate(sorted(frames_dir.glob("*.jpg"))):
            records.append(
                {
                    "frame_path": str(frame_path.resolve()),
                    "gaze_yaw": meta.get("gaze", {}).get("yaw", 0.0),
                    "gaze_pitch": meta.get("gaze", {}).get("pitch", 0.0),
                    "head_yaw": meta.get("head_pose", {}).get("yaw", 0.0),
                    "head_pitch": meta.get("head_pose", {}).get("pitch", 0.0),
                    "eyes_open_prob": meta.get("eyes_open_prob", 0.95),
                    "label": label,
                    "confidence": meta.get("confidence", 0.9),
                    "meta": {
                        "session": session_dir.name,
                        "frame_index": idx,
                        "timestamp": meta.get("timestamp", datetime.utcnow().isoformat()),
                    },
                }
            )
            if limit and len(records) >= limit:
                break
        if limit and len(records) >= limit:
            break

    _write_metadata(records, output_dir)
    print(f"[local_calibration] wrote {len(records)} entries to {output_dir}")


def synthetic_demo_adapter(
    spec: DatasetSpec,
    raw_dir: Path,
    output_dir: Path,
    limit: Optional[int] = 512,
):
    """
    Generate synthetic samples for CI / documentation.
    Produces blank images with metadata describing gaze/pose targets.
    """

    _ensure_dir(output_dir)
    frames_dir = output_dir / "frames"
    _ensure_dir(frames_dir)
    records = []

    labels = [
        "focused",
        "looking_left",
        "looking_right",
        "looking_up",
        "looking_down",
        "sleepy",
        "partial_engaged",
        "no_face",
    ]

    for idx in range(limit or 256):
        label = random.choice(labels)
        frame_path = frames_dir / f"synthetic_{idx:05d}.jpg"
        if cv2 is not None:
            img = np.zeros((120, 160, 3), dtype=np.uint8)
            cv2.putText(
                img,
                label[:8],
                (5, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.imwrite(str(frame_path), img)
        else:
            frame_path.write_bytes(b"synthetic")

        yaw = random.uniform(-25, 25)
        pitch = random.uniform(-15, 15)
        head_yaw = yaw + random.uniform(-3, 3)
        head_pitch = pitch + random.uniform(-3, 3)

        records.append(
            {
                "frame_path": str(frame_path.resolve()),
                "gaze_yaw": yaw,
                "gaze_pitch": pitch,
                "head_yaw": head_yaw,
                "head_pitch": head_pitch,
                "eyes_open_prob": 0.2 if label == "sleepy" else 0.95,
                "label": label,
                "confidence": 0.8,
                "meta": {"source": "synthetic"},
            }
        )

    _write_metadata(records, output_dir)
    print(f"[synthetic_demo] generated {len(records)} samples in {output_dir}")


ADAPTERS = {
    "local_calibration": local_calibration_adapter,
    "synthetic_demo": synthetic_demo_adapter,
    # Stubs for real datasets; raise NotImplementedError until contributed.
    "gazecapture": adapter_not_implemented,
    "mpiigaze": adapter_not_implemented,
    "columbia": adapter_not_implemented,
    "ethxgaze": adapter_not_implemented,
    "openeds": adapter_not_implemented,
}


