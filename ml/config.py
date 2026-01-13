"""
Configuration utilities for Focus Mate training pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class TrainingConfig:
    data_path: Path
    output_dir: Path = Path("artifacts/model")
    epochs: int = 5
    batch_size: int = 32
    learning_rate: float = 2e-4
    image_size: tuple[int, int] = (120, 160)  # (height, width) for TensorFlow
    label_smoothing: float = 0.05
    num_workers: int = 4
    logging_interval: int = 50
    checkpoint_interval: int = 1
    use_gpu: bool = True
    mixed_precision: bool = False
    sample_labels: tuple[str, ...] = (
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
    )
    
    def __post_init__(self):
        """Configure device settings."""
        if not self.use_gpu:
            # Force CPU mode
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        
        # Auto-detect GPU availability
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            if gpus and self.use_gpu:
                print(f"[Focus Mate Config] Found {len(gpus)} GPU(s)")
                if self.mixed_precision:
                    tf.keras.mixed_precision.set_global_policy('mixed_float16')
                    print("[Focus Mate Config] Mixed precision enabled")
            else:
                print("[Focus Mate Config] Running on CPU")
                self.use_gpu = False
        except ImportError:
            print("[Focus Mate Config] TensorFlow not available")


def ensure_output_dirs(cfg: TrainingConfig) -> None:
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    (cfg.output_dir / "checkpoints").mkdir(exist_ok=True)
    (cfg.output_dir / "logs").mkdir(exist_ok=True)


