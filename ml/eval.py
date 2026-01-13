"""
Focus Mate - Model Evaluation Script

Evaluates trained model on test dataset and computes metrics:
- Per-label precision, recall, F1
- Gaze angle MAE (mean absolute error)
- Head pose MAE
- Eye openness accuracy
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import tensorflow as tf

try:
    import cv2
except Exception:
    cv2 = None

from ml.config import TrainingConfig
from ml.dataset import load_samples, train_val_split
from ml.labels import LABELS, LABEL_TO_INDEX


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, task: str) -> Dict[str, float]:
    """Compute metrics for a specific task."""
    metrics = {}
    
    if task == "classification":
        # Per-class metrics
        for i, label in enumerate(LABELS):
            true_pos = np.sum((y_true == i) & (y_pred == i))
            false_pos = np.sum((y_true != i) & (y_pred == i))
            false_neg = np.sum((y_true == i) & (y_pred != i))
            
            precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
            recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            metrics[f"{label}_precision"] = precision
            metrics[f"{label}_recall"] = recall
            metrics[f"{label}_f1"] = f1
        
        # Overall accuracy
        metrics["accuracy"] = np.mean(y_true == y_pred)
        
        # Macro-averaged F1
        f1_scores = [metrics[f"{label}_f1"] for label in LABELS]
        metrics["macro_f1"] = np.mean(f1_scores)
        
    elif task == "regression":
        # MAE (Mean Absolute Error)
        metrics["mae"] = np.mean(np.abs(y_true - y_pred))
        # RMSE (Root Mean Squared Error)
        metrics["rmse"] = np.sqrt(np.mean((y_true - y_pred) ** 2))
        # R² score
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        metrics["r2"] = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
    return metrics


def evaluate_model(model_path: Path, data_path: Path, output_path: Path | None = None):
    """Evaluate model and save metrics."""
    print(f"[Focus Mate Eval] Loading model from {model_path}")
    model = tf.keras.models.load_model(str(model_path))
    
    print(f"[Focus Mate Eval] Loading test data from {data_path}")
    samples = load_samples(data_path)
    _, test_samples = train_val_split(samples, val_ratio=0.2)
    
    if not test_samples:
        raise RuntimeError("No test samples available")
    
    print(f"[Focus Mate Eval] Evaluating on {len(test_samples)} samples")
    
    # Prepare test data
    images = []
    gaze_yaw_true = []
    gaze_pitch_true = []
    head_yaw_true = []
    head_pitch_true = []
    eyes_open_true = []
    labels_true = []
    
    for sample in test_samples:
        if cv2:
            img = cv2.resize(sample.image, (160, 120))
            images.append(img.astype("float32") / 255.0)
        else:
            images.append(np.zeros((120, 160, 3), dtype="float32"))
        
        gaze_yaw_true.append(sample.gaze_yaw)
        gaze_pitch_true.append(sample.gaze_pitch)
        head_yaw_true.append(sample.head_yaw)
        head_pitch_true.append(sample.head_pitch)
        eyes_open_true.append(sample.eyes_open_prob)
        labels_true.append(LABEL_TO_INDEX.get(sample.label, LABEL_TO_INDEX["unknown"]))
    
    images_arr = np.array(images)
    
    # Run inference
    print("[Focus Mate Eval] Running inference...")
    predictions = model.predict(images_arr, verbose=0)
    
    # Extract predictions
    gaze_yaw_pred = predictions[0].flatten()
    gaze_pitch_pred = predictions[1].flatten()
    head_yaw_pred = predictions[2].flatten()
    head_pitch_pred = predictions[3].flatten()
    eyes_open_pred = predictions[4].flatten()
    label_probs = predictions[5]
    labels_pred = np.argmax(label_probs, axis=1)
    
    # Compute metrics
    print("\n[Focus Mate Eval] Computing metrics...")
    
    metrics = {
        "gaze_yaw": compute_metrics(np.array(gaze_yaw_true), gaze_yaw_pred, "regression"),
        "gaze_pitch": compute_metrics(np.array(gaze_pitch_true), gaze_pitch_pred, "regression"),
        "head_yaw": compute_metrics(np.array(head_yaw_true), head_yaw_pred, "regression"),
        "head_pitch": compute_metrics(np.array(head_pitch_true), head_pitch_pred, "regression"),
        "eyes_open": {
            "mae": np.mean(np.abs(np.array(eyes_open_true) - eyes_open_pred)),
            "accuracy": np.mean((np.array(eyes_open_true) > 0.5) == (eyes_open_pred > 0.5)),
        },
        "labels": compute_metrics(np.array(labels_true), labels_pred, "classification"),
    }
    
    # Print results
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    
    print("\n📊 Gaze Estimation:")
    print(f"  Yaw MAE:   {metrics['gaze_yaw']['mae']:.2f}°")
    print(f"  Pitch MAE: {metrics['gaze_pitch']['mae']:.2f}°")
    
    print("\n📊 Head Pose Estimation:")
    print(f"  Yaw MAE:   {metrics['head_yaw']['mae']:.2f}°")
    print(f"  Pitch MAE: {metrics['head_pitch']['mae']:.2f}°")
    
    print("\n📊 Eye Openness:")
    print(f"  MAE:      {metrics['eyes_open']['mae']:.3f}")
    print(f"  Accuracy: {metrics['eyes_open']['accuracy']*100:.1f}%")
    
    print("\n📊 Attention Classification:")
    print(f"  Overall Accuracy: {metrics['labels']['accuracy']*100:.1f}%")
    print(f"  Macro F1:         {metrics['labels']['macro_f1']:.3f}")
    
    print("\n📊 Per-Label Performance:")
    for label in LABELS:
        f1 = metrics['labels'][f'{label}_f1']
        precision = metrics['labels'][f'{label}_precision']
        recall = metrics['labels'][f'{label}_recall']
        print(f"  {label:25s} - F1: {f1:.3f}  P: {precision:.3f}  R: {recall:.3f}")
    
    # Save metrics
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"\n✓ Metrics saved to {output_path}")
    
    print("\n" + "="*60)
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate Focus Mate attention model")
    parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Path to saved model directory"
    )
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Path to test data metadata.jsonl"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to save metrics JSON (optional)"
    )
    args = parser.parse_args()
    
    evaluate_model(args.model, args.data, args.output)


if __name__ == "__main__":
    main()
