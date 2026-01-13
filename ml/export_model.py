"""
Focus Mate - Export SavedModel to TF Lite, TF.js, and ONNX formats.
Includes quantization for lightweight browser inference.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import tensorflow as tf


def export_tflite(saved_model_dir: Path, target_dir: Path, quantize: bool = True) -> Path:
    """
    Export model to TensorFlow Lite format with optional quantization.
    
    Args:
        saved_model_dir: Path to SavedModel directory
        target_dir: Output directory for TFLite model
        quantize: Whether to apply quantization (reduces model size)
    
    Returns:
        Path to exported .tflite file
    """
    print(f"[Focus Mate Export] Converting to TF Lite (quantize={quantize})...")
    converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    
    if quantize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
    
    tflite_model = converter.convert()
    target_dir.mkdir(parents=True, exist_ok=True)
    
    filename = "focusmate-attention-quantized.tflite" if quantize else "focusmate-attention.tflite"
    tflite_path = target_dir / filename
    tflite_path.write_bytes(tflite_model)
    
    size_mb = len(tflite_model) / (1024 * 1024)
    print(f"[Focus Mate Export] ✓ TF Lite saved to {tflite_path} ({size_mb:.2f} MB)")
    return tflite_path


def export_tfjs(saved_model_dir: Path, target_dir: Path, quantize: bool = True) -> Path:
    """
    Export model to TensorFlow.js format for browser inference.
    
    Args:
        saved_model_dir: Path to SavedModel directory
        target_dir: Output directory for TF.js model
        quantize: Whether to apply quantization
    
    Returns:
        Path to exported TF.js directory
    """
    print("[Focus Mate Export] Converting to TensorFlow.js...")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Use tensorflowjs_converter command line tool instead of Python API
    import subprocess
    
    cmd = [
        "tensorflowjs_converter",
        "--input_format=tf_saved_model",
        "--output_format=tfjs_graph_model",
    ]
    
    if quantize:
        cmd.append("--quantize_uint8=*")
    
    cmd.extend([str(saved_model_dir), str(target_dir)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[Focus Mate Export] ✗ TF.js export failed: {result.stderr}")
        raise RuntimeError(f"TF.js export failed: {result.stderr}")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in target_dir.glob("**/*") if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    print(f"[Focus Mate Export] ✓ TF.js saved to {target_dir} ({size_mb:.2f} MB)")
    print(f"[Focus Mate Export]   Load in browser: tf.loadLayersModel('{target_dir}/model.json')")
    return target_dir


def export_onnx(saved_model_dir: Path, target_dir: Path) -> Path:
    """
    Export model to ONNX format (optional, requires tf2onnx).
    
    Args:
        saved_model_dir: Path to SavedModel directory
        target_dir: Output directory for ONNX model
    
    Returns:
        Path to exported .onnx file
    """
    try:
        import tf2onnx
    except ImportError:
        print("[Focus Mate Export] ⚠ tf2onnx not installed, skipping ONNX export")
        print("                     Install with: pip install tf2onnx")
        return None
    
    print("[Focus Mate Export] Converting to ONNX...")
    target_dir.mkdir(parents=True, exist_ok=True)
    onnx_path = target_dir / "focusmate-attention.onnx"
    
    # Convert using tf2onnx
    import subprocess
    result = subprocess.run([
        "python", "-m", "tf2onnx.convert",
        "--saved-model", str(saved_model_dir),
        "--output", str(onnx_path),
        "--opset", "13",
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        size_mb = onnx_path.stat().st_size / (1024 * 1024)
        print(f"[Focus Mate Export] ✓ ONNX saved to {onnx_path} ({size_mb:.2f} MB)")
        return onnx_path
    else:
        print(f"[Focus Mate Export] ✗ ONNX export failed: {result.stderr}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Export Focus Mate attention model to TF Lite, TF.js, and ONNX formats"
    )
    parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Path to SavedModel directory (e.g., artifacts/focusmate_model/saved_model)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output directory for exports (e.g., frontend/public/models/focusmate-attention)"
    )
    parser.add_argument(
        "--no-quantize",
        action="store_true",
        help="Disable quantization (larger model size, slightly better accuracy)"
    )
    parser.add_argument(
        "--format",
        choices=["all", "tflite", "tfjs", "onnx"],
        default="all",
        help="Export format (default: all)"
    )
    args = parser.parse_args()

    if not args.model.exists():
        raise FileNotFoundError(f"Model not found: {args.model}")
    
    quantize = not args.no_quantize
    
    print(f"\n[Focus Mate Export] Exporting model from {args.model}")
    print(f"[Focus Mate Export] Output directory: {args.out}")
    print(f"[Focus Mate Export] Quantization: {'enabled' if quantize else 'disabled'}\n")
    
    if args.format in ["all", "tflite"]:
        tflite_dir = args.out / "tflite"
        export_tflite(args.model, tflite_dir, quantize=quantize)
    
    if args.format in ["all", "tfjs"]:
        tfjs_dir = args.out / "tfjs"
        export_tfjs(args.model, tfjs_dir, quantize=quantize)
    
    if args.format in ["all", "onnx"]:
        onnx_dir = args.out / "onnx"
        export_onnx(args.model, onnx_dir)
    
    print("\n[Focus Mate Export] ✓ Export complete!")
    print("\nNext steps:")
    print("  1. Copy TF.js model to frontend/public/models/")
    print("  2. Update VideoProcessor to load the model")
    print("  3. Test inference in the browser")


if __name__ == "__main__":
    main()
