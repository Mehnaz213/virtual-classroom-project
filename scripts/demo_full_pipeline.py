#!/usr/bin/env python3
"""
Focus Mate - Full Pipeline Demo

Demonstrates the complete ML pipeline:
1. Generate synthetic training data
2. Train model
3. Evaluate model
4. Export to TF.js
5. Test inference

This script is useful for:
- Testing the complete pipeline
- CI/CD validation
- Quick demos
- Development testing
"""

import subprocess
import sys
from pathlib import Path
import time

def run_command(cmd: list[str], description: str):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"[Focus Mate Demo] {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True)
    elapsed = time.time() - start_time
    
    if result.returncode != 0:
        print(f"\n✗ Failed: {description}")
        print(f"  Exit code: {result.returncode}")
        sys.exit(1)
    
    print(f"\n✓ Completed in {elapsed:.1f}s: {description}")
    return result


def main():
    print("\n" + "="*60)
    print("Focus Mate - Full Pipeline Demo")
    print("="*60)
    print("\nThis will:")
    print("  1. Generate 500 synthetic training samples")
    print("  2. Train model for 3 epochs (quick demo)")
    print("  3. Evaluate model performance")
    print("  4. Export to TF.js format")
    print("  5. Show results")
    print("\nEstimated time: 5-10 minutes (CPU) or 2-3 minutes (GPU)")
    
    response = input("\nContinue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Paths
    data_dir = Path("data/processed/demo_pipeline")
    model_dir = Path("artifacts/demo_model")
    export_dir = Path("frontend/public/models/demo")
    
    # Step 1: Generate synthetic data
    run_command([
        sys.executable,
        "ml/data_ingest.py",
        "ingest",
        "synthetic_demo",
        "--limit", "500",
        "--output", str(data_dir.parent),
    ], "Generate synthetic training data")
    
    # Step 2: Train model
    run_command([
        sys.executable,
        "ml/train.py",
        "--data", str(data_dir / "metadata.jsonl"),
        "--output", str(model_dir),
        "--epochs", "3",
        "--batch-size", "16",
    ], "Train attention detection model")
    
    # Step 3: Evaluate model
    run_command([
        sys.executable,
        "ml/eval.py",
        "--model", str(model_dir / "saved_model"),
        "--data", str(data_dir / "metadata.jsonl"),
        "--output", str(model_dir / "metrics.json"),
    ], "Evaluate model performance")
    
    # Step 4: Export to TF.js
    run_command([
        sys.executable,
        "ml/export_model.py",
        "--model", str(model_dir / "saved_model"),
        "--out", str(export_dir),
        "--format", "tfjs",
    ], "Export model to TF.js")
    
    # Step 5: Show results
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    
    print("\n📊 Results:")
    print(f"  Model:   {model_dir / 'saved_model'}")
    print(f"  Metrics: {model_dir / 'metrics.json'}")
    print(f"  TF.js:   {export_dir / 'tfjs'}")
    
    print("\n📚 Next steps:")
    print("  1. Review metrics in metrics.json")
    print("  2. Start frontend: cd frontend && npm run dev")
    print("  3. Model will be loaded automatically")
    print("  4. Test with webcam in student view")
    
    print("\n💡 Tips:")
    print("  - For better accuracy, train with more data")
    print("  - Use real datasets (GazeCapture, MPIIGaze, etc.)")
    print("  - Train for more epochs (10-20)")
    print("  - Use GPU for faster training")
    
    print("\n✓ Demo pipeline completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
