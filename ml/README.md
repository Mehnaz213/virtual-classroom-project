# Focus Mate ML Pipeline

Advanced attention detection model for Focus Mate.

## Quick Start

```bash
# Generate synthetic training data
python data_ingest.py ingest synthetic_demo --limit 1000

# Train model
python train.py --data data/processed/synthetic_demo/metadata.jsonl --epochs 10

# Export for browser
python export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out ../frontend/public/models/focusmate-attention \
  --format tfjs
```

## Attention Labels (11 States)

- `focused` - Looking at screen
- `looking_left` / `looking_right` / `looking_up` / `looking_down`
- `engaged` / `partial_engaged`
- `sleepy` - Eyes closing
- `distracted_by_multi_face` / `no_face` / `unknown`

## Model Architecture

- **Base**: MobileNetV3-Small
- **Input**: 160×120×3 RGB
- **Outputs**: Gaze (yaw/pitch), Head pose (yaw/pitch), Eye openness, Labels
- **Size**: <10MB quantized

## Supported Datasets

- GazeCapture, MPIIGaze, Columbia Gaze, ETH-XGaze, OpenEDS
- Synthetic demo data
- Local calibration captures

See main README and docs/FEATURES.md for complete documentation.
