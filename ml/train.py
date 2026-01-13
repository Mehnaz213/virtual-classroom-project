"""
Focus Mate - Training entry point for advanced attention detection model.
Supports detailed attention states including gaze direction, sleepiness, and engagement levels.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf

try:
    import cv2
except Exception as exc:  # pragma: no cover
    raise RuntimeError("OpenCV (cv2) is required for training. Install opencv-python.") from exc

from ml.config import TrainingConfig, ensure_output_dirs
from ml.dataset import load_samples, train_val_split
from ml.labels import LABELS, LABEL_TO_INDEX
from ml.model import build_model


def preprocess_samples(samples, image_size):
    """
    Preprocess training samples into model-ready format.
    
    Returns:
        dict with 'images' and 'targets' for multi-head model training
    """
    images = []
    gaze_yaw = []
    gaze_pitch = []
    head_yaw = []
    head_pitch = []
    eyes_open = []
    label_vectors = []

    for sample in samples:
        # cv2.resize expects (width, height), but image_size is (height, width)
        img = cv2.resize(sample.image, (image_size[1], image_size[0]))
        images.append(img.astype("float32") / 255.0)
        gaze_yaw.append(sample.gaze_yaw)
        gaze_pitch.append(sample.gaze_pitch)
        head_yaw.append(sample.head_yaw)
        head_pitch.append(sample.head_pitch)
        eyes_open.append(sample.eyes_open_prob)
        vec = np.zeros(len(LABELS), dtype="float32")
        vec[LABEL_TO_INDEX.get(sample.label, LABEL_TO_INDEX["unknown"])] = 1.0
        label_vectors.append(vec)

    return {
        "images": np.array(images),
        "targets": {
            "gaze_yaw": np.array(gaze_yaw),
            "gaze_pitch": np.array(gaze_pitch),
            "head_yaw": np.array(head_yaw),
            "head_pitch": np.array(head_pitch),
            "eyes_open_prob": np.array(eyes_open),
            "label_probs": np.array(label_vectors),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Train Focus Mate gaze/attention model")
    parser.add_argument("--data", type=Path, required=True, help="metadata.jsonl path")
    parser.add_argument("--output", type=Path, default=Path("artifacts/focusmate_model"))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--cpu", action="store_true", help="Force CPU mode (no GPU)")
    parser.add_argument("--mixed-precision", action="store_true", help="Enable mixed precision training")
    args = parser.parse_args()

    cfg = TrainingConfig(
        data_path=args.data,
        output_dir=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        use_gpu=not args.cpu,
        mixed_precision=args.mixed_precision,
    )
    ensure_output_dirs(cfg)

    print(f"[Focus Mate Train] Loading samples from {cfg.data_path}")
    samples = load_samples(cfg.data_path)
    train_samples, val_samples = train_val_split(samples)
    
    if not train_samples or not val_samples:
        raise RuntimeError(
            "Not enough samples to train. Please run data ingestion first:\n"
            "  python ml/data_ingest.py ingest synthetic_demo --limit 500"
        )

    print(f"[Focus Mate Train] Training samples: {len(train_samples)}, Validation: {len(val_samples)}")
    
    train_data = preprocess_samples(train_samples, cfg.image_size)
    val_data = preprocess_samples(val_samples, cfg.image_size)

    print("[Focus Mate Train] Building MobileNetV3 multi-head model...")
    model = build_model(input_shape=(*cfg.image_size, 3), num_labels=len(LABELS))
    
    print(f"[Focus Mate Train] Model summary:")
    model.summary()

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(cfg.output_dir / "checkpoints" / "model.{epoch:02d}.keras"),
            save_best_only=True,
            monitor="val_label_probs_accuracy",
        ),
        tf.keras.callbacks.TensorBoard(log_dir=str(cfg.output_dir / "logs")),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_label_probs_accuracy",
            patience=3,
            restore_best_weights=True,
        ),
    ]

    print(f"[Focus Mate Train] Starting training for {cfg.epochs} epochs...")
    history = model.fit(
        train_data["images"],
        train_data["targets"],
        validation_data=(val_data["images"], val_data["targets"]),
        epochs=cfg.epochs,
        batch_size=cfg.batch_size,
        callbacks=callbacks,
    )

    saved_model_path = cfg.output_dir / "saved_model"
    model.save(saved_model_path)
    print(f"[Focus Mate Train] ✓ Model saved to {saved_model_path}")
    
    # Print final metrics
    print("\n[Focus Mate Train] Final metrics:")
    for key, value in history.history.items():
        if key.startswith("val_"):
            print(f"  {key}: {value[-1]:.4f}")


if __name__ == "__main__":
    main()
