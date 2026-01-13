"""
Focus Mate - Dataset ingestion and normalization.

Supports multiple public gaze/attention datasets:
- GazeCapture (MIT)
- MPIIGaze
- Columbia Gaze
- ETH-XGaze
- OpenEDS
- Synthetic demo data
- Local calibration captures

All datasets are normalized to a unified JSONL format with:
- frame_path, gaze_yaw, gaze_pitch, head_yaw, head_pitch
- eyes_open_prob, label, confidence, metadata
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np

# TODO: Add actual dataset adapters once archives are downloaded
DATASETS = {
    "gaze_capture": {
        "url": "https://gazecapture.csail.mit.edu/",
        "license": "Research-only (request access)",
        "notes": "Mobile-focused dataset for on-screen vs. off-screen attention",
    },
    "mpiigaze": {
        "url": "https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/gaze-estimation/mpiigaze",
        "license": "Non-commercial (request access)",
        "notes": "Laptop gaze/head-pose diversity",
    },
    "columbia_gaze": {
        "url": "http://www.cs.columbia.edu/CAVE/databases/columbia_gaze/",
        "license": "Non-commercial (direct download)",
        "notes": "Discrete left/right/up/down gaze samples",
    },
    "eth_xgaze": {
        "url": "https://ait.ethz.ch/projects/2020/xgaze/",
        "license": "Research-only (request access)",
        "notes": "Large multi-view head-pose dataset",
    },
    "openeds": {
        "url": "https://research.fb.com/openeds-2020-challenge/",
        "license": "CC BY-NC 4.0 (registration required)",
        "notes": "Eye segmentation / eye-openness cues",
    },
}

ATTENTION_LABELS = [
    "focused",
    "looking_left",
    "looking_right",
    "looking_up",
    "looking_down",
    "engaged",
    "partial_engaged",
    "sleepy",
    "distracted_by_multi_face",
    "no_face",
    "unknown",
]


@dataclass
class UnifiedSample:
    """Unified sample format for all datasets."""
    frame_path: str
    gaze_yaw: float
    gaze_pitch: float
    head_yaw: float
    head_pitch: float
    eyes_open_prob: float
    label: str
    confidence: float
    meta: dict


def generate_synthetic_samples(count: int, output_dir: Path) -> List[UnifiedSample]:
    """
    Generate synthetic training samples for testing/CI.
    Creates realistic gaze angles and labels for each attention state.
    """
    print(f"[Focus Mate Ingest] Generating {count} synthetic samples...")
    
    samples = []
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(count):
        # Randomly select a label
        label = random.choice(ATTENTION_LABELS)
        
        # Generate realistic gaze/head pose based on label
        if label == "focused":
            gaze_yaw, gaze_pitch = random.gauss(0, 2), random.gauss(0, 2)
            head_yaw, head_pitch = random.gauss(0, 3), random.gauss(0, 3)
            eyes_open = random.uniform(0.8, 1.0)
        elif label == "looking_left":
            gaze_yaw, gaze_pitch = random.gauss(-15, 3), random.gauss(0, 2)
            head_yaw, head_pitch = random.gauss(-10, 3), random.gauss(0, 3)
            eyes_open = random.uniform(0.7, 1.0)
        elif label == "looking_right":
            gaze_yaw, gaze_pitch = random.gauss(15, 3), random.gauss(0, 2)
            head_yaw, head_pitch = random.gauss(10, 3), random.gauss(0, 3)
            eyes_open = random.uniform(0.7, 1.0)
        elif label == "looking_up":
            gaze_yaw, gaze_pitch = random.gauss(0, 2), random.gauss(10, 3)
            head_yaw, head_pitch = random.gauss(0, 3), random.gauss(8, 3)
            eyes_open = random.uniform(0.7, 1.0)
        elif label == "looking_down":
            gaze_yaw, gaze_pitch = random.gauss(0, 2), random.gauss(-10, 3)
            head_yaw, head_pitch = random.gauss(0, 3), random.gauss(-8, 3)
            eyes_open = random.uniform(0.7, 1.0)
        elif label == "sleepy":
            gaze_yaw, gaze_pitch = random.gauss(0, 5), random.gauss(-5, 3)
            head_yaw, head_pitch = random.gauss(0, 5), random.gauss(-5, 3)
            eyes_open = random.uniform(0.0, 0.3)
        elif label == "engaged":
            gaze_yaw, gaze_pitch = random.gauss(0, 5), random.gauss(0, 5)
            head_yaw, head_pitch = random.gauss(0, 5), random.gauss(0, 5)
            eyes_open = random.uniform(0.7, 1.0)
        else:
            gaze_yaw, gaze_pitch = random.gauss(0, 10), random.gauss(0, 10)
            head_yaw, head_pitch = random.gauss(0, 10), random.gauss(0, 10)
            eyes_open = random.uniform(0.5, 1.0)
        
        # Create synthetic image (placeholder)
        frame_path = f"frames/synthetic_{i:05d}.jpg"
        
        # Generate synthetic image data (height, width, channels)
        img = np.random.randint(0, 255, (120, 160, 3), dtype=np.uint8)
        try:
            import cv2
            cv2.imwrite(str(output_dir / frame_path), img)
        except ImportError:
            pass  # Skip image writing if cv2 not available
        
        samples.append(UnifiedSample(
            frame_path=frame_path,
            gaze_yaw=gaze_yaw,
            gaze_pitch=gaze_pitch,
            head_yaw=head_yaw,
            head_pitch=head_pitch,
            eyes_open_prob=eyes_open,
            label=label,
            confidence=random.uniform(0.7, 0.95),
            meta={"source": "synthetic", "index": i},
        ))
    
    return samples


def write_metadata_jsonl(samples: List[UnifiedSample], output_path: Path):
    """Write samples to JSONL metadata file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        for sample in samples:
            record = {
                "frame_path": sample.frame_path,
                "gaze_yaw": sample.gaze_yaw,
                "gaze_pitch": sample.gaze_pitch,
                "head_yaw": sample.head_yaw,
                "head_pitch": sample.head_pitch,
                "eyes_open_prob": sample.eyes_open_prob,
                "label": sample.label,
                "confidence": sample.confidence,
                "meta": sample.meta,
            }
            f.write(json.dumps(record) + "\n")
    
    print(f"[Focus Mate Ingest] ✓ Wrote {len(samples)} samples to {output_path}")


def list_datasets():
    """List available datasets with URLs and licensing info."""
    print("\n[Focus Mate Ingest] Available datasets:\n")
    for name, info in DATASETS.items():
        print(f"  {name}")
        print(f"    URL: {info['url']}")
        print(f"    License: {info['license']}")
        print(f"    Notes: {info['notes']}\n")
    
    print("To use these datasets:")
    print("  1. Request access / download from the URLs above")
    print("  2. Place archives in data/raw/<dataset_name>/")
    print("  3. Implement adapter in ml/data_ingest.py")
    print("  4. Run: python ml/data_ingest.py ingest <dataset_name>")


def main():
    parser = argparse.ArgumentParser(
        description="Focus Mate dataset ingestion and normalization"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    subparsers.add_parser("list", help="List available datasets")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a dataset")
    ingest_parser.add_argument(
        "dataset",
        choices=["synthetic_demo", "local_calibration"] + list(DATASETS.keys()),
        help="Dataset to ingest"
    )
    ingest_parser.add_argument(
        "--raw",
        type=Path,
        help="Path to raw dataset files"
    )
    ingest_parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed"),
        help="Output directory for processed data"
    )
    ingest_parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of samples (for testing)"
    )
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_datasets()
        return
    
    if args.command == "ingest":
        output_dir = args.output / args.dataset
        
        if args.dataset == "synthetic_demo":
            # Generate synthetic data
            count = args.limit or 1000
            samples = generate_synthetic_samples(count, output_dir)
            write_metadata_jsonl(samples, output_dir / "metadata.jsonl")
            
        elif args.dataset == "local_calibration":
            # TODO: Implement local calibration data ingestion
            print("[Focus Mate Ingest] Local calibration ingestion not yet implemented")
            print("                     Use scripts/local_capture/capture_cli.py to collect data")
            
        else:
            # Public dataset ingestion
            if not args.raw:
                print(f"[Focus Mate Ingest] Error: --raw path required for {args.dataset}")
                print(f"                     Download from: {DATASETS[args.dataset]['url']}")
                return
            
            print(f"[Focus Mate Ingest] TODO: Implement adapter for {args.dataset}")
            print(f"                     Raw data: {args.raw}")
            print(f"                     Output: {output_dir}")
            print("\nAdapter implementation needed:")
            print("  1. Parse dataset-specific format")
            print("  2. Extract gaze angles, head pose, eye openness")
            print("  3. Map to Focus Mate attention labels")
            print("  4. Write to unified JSONL format")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
