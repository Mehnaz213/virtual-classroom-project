# Focus Mate - AI Training & Real-Time Monitoring Guide

Complete guide for training and deploying the Focus Mate attention detection model.

## 🎯 Overview

Focus Mate uses a lightweight MobileNetV3-based model that predicts:
- **Gaze direction** (yaw/pitch angles)
- **Head pose** (yaw/pitch angles)
- **Eye openness** (0-1 probability)
- **Attention labels** (11 categories)

The model runs **client-side in the browser** using TensorFlow.js for privacy.

## 🚀 Quick Start (5 Minutes)

### Option 1: Automated Demo Pipeline

```bash
python scripts/demo_full_pipeline.py
```

This will:
1. Generate 500 synthetic samples
2. Train model for 3 epochs
3. Evaluate performance
4. Export to TF.js
5. Show results

### Option 2: Manual Steps

```bash
# 1. Generate training data
python ml/data_ingest.py ingest synthetic_demo --limit 1000

# 2. Train model
python ml/train.py \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --epochs 10 \
  --batch-size 32

# 3. Evaluate
python ml/eval.py \
  --model artifacts/focusmate_model/saved_model \
  --data data/processed/synthetic_demo/metadata.jsonl

# 4. Export to TF.js
python ml/export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out frontend/public/models/focusmate-attention \
  --format tfjs
```

## 📊 Datasets

### Supported Public Datasets

| Dataset | Size | License | Best For |
|---------|------|---------|----------|
| **GazeCapture** | 2.5M frames | Research-only | Mobile gaze, on/off screen |
| **MPIIGaze** | 213K frames | Non-commercial | Laptop gaze, head pose |
| **Columbia Gaze** | 5,880 images | Non-commercial | Discrete gaze directions |
| **ETH-XGaze** | 1M frames | Research-only | Multi-view head pose |
| **OpenEDS** | 12K sequences | CC BY-NC 4.0 | Eye segmentation, openness |

### Dataset Access

1. **Request Access:**
   - GazeCapture: https://gazecapture.csail.mit.edu/
   - MPIIGaze: https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/gaze-estimation/mpiigaze
   - Columbia Gaze: http://www.cs.columbia.edu/CAVE/databases/columbia_gaze/
   - ETH-XGaze: https://ait.ethz.ch/projects/2020/xgaze/
   - OpenEDS: https://research.fb.com/openeds-2020-challenge/

2. **Download & Extract:**
   ```bash
   mkdir -p data/raw/<dataset_name>
   # Extract archives to data/raw/<dataset_name>/
   ```

3. **Ingest Dataset:**
   ```bash
   python ml/data_ingest.py ingest <dataset_name> \
     --raw data/raw/<dataset_name> \
     --output data/processed
   ```

### Synthetic Data (For Testing)

```bash
# Generate synthetic samples
python ml/data_ingest.py ingest synthetic_demo \
  --limit 1000 \
  --output data/processed
```

Synthetic data includes:
- Realistic gaze angles per label
- Varied head poses
- Eye openness variations
- All 11 attention labels

## 🏋️ Training

### Basic Training

```bash
python ml/train.py \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --output artifacts/focusmate_model \
  --epochs 10 \
  --batch-size 32
```

### CPU Mode (No GPU)

```bash
python ml/train.py \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --epochs 10 \
  --cpu
```

### GPU Mode with Mixed Precision

```bash
python ml/train.py \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --epochs 20 \
  --batch-size 64 \
  --mixed-precision
```

### Training Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--data` | Required | Path to metadata.jsonl |
| `--output` | artifacts/focusmate_model | Output directory |
| `--epochs` | 10 | Number of training epochs |
| `--batch-size` | 32 | Batch size |
| `--cpu` | False | Force CPU mode |
| `--mixed-precision` | False | Enable mixed precision (GPU only) |

### Expected Training Time

| Hardware | Samples | Epochs | Time |
|----------|---------|--------|------|
| CPU (8 cores) | 1,000 | 10 | ~15 min |
| GPU (RTX 3060) | 1,000 | 10 | ~3 min |
| CPU (8 cores) | 10,000 | 20 | ~4 hours |
| GPU (RTX 3060) | 10,000 | 20 | ~30 min |

## 📈 Evaluation

```bash
python ml/eval.py \
  --model artifacts/focusmate_model/saved_model \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --output artifacts/focusmate_model/metrics.json
```

### Metrics Computed

**Regression Tasks:**
- Gaze yaw/pitch MAE (degrees)
- Head pose yaw/pitch MAE (degrees)
- Eye openness MAE

**Classification:**
- Per-label precision, recall, F1
- Overall accuracy
- Macro-averaged F1

### Target Performance

| Metric | Target | Good | Excellent |
|--------|--------|------|-----------|
| Label Accuracy | >70% | >80% | >90% |
| Gaze MAE | <10° | <5° | <3° |
| Head Pose MAE | <15° | <10° | <5° |
| Eye Openness Acc | >80% | >90% | >95% |

## 📦 Model Export

### TensorFlow.js (Browser)

```bash
python ml/export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out frontend/public/models/focusmate-attention \
  --format tfjs
```

### TensorFlow Lite (Mobile)

```bash
python ml/export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out frontend/public/models/focusmate-attention \
  --format tflite
```

### ONNX (Cross-platform)

```bash
# Requires tf2onnx: pip install tf2onnx
python ml/export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out frontend/public/models/focusmate-attention \
  --format onnx
```

### Quantization

By default, models are quantized to reduce size:
- Float16 quantization for TFLite
- Weight quantization for TF.js
- Target size: <10MB

Disable quantization:
```bash
python ml/export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out frontend/public/models/focusmate-attention \
  --format tfjs \
  --no-quantize
```

## 🌐 Frontend Integration

### Automatic Loading

The frontend automatically loads the model from:
```
frontend/public/models/focusmate-attention/tfjs/model.json
```

### Manual Testing

1. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Login as Student:**
   - Go to http://localhost:5173
   - Login with student credentials
   - Join a session

3. **Test Inference:**
   - Allow webcam access
   - Look in different directions
   - Check console for inference logs
   - Verify labels update in real-time

### Fallback Behavior

If model fails to load:
- System falls back to heuristic detection
- Uses MediaPipe landmarks
- Simple rule-based classification
- No accuracy loss for basic features

## 📊 Real-Time Dashboard

### Teacher Dashboard Features

**Timeline Graph:**
- Color-coded markers for each label
- Hover for details
- Zoom and pan
- Export data

**Aggregated Stats:**
- Percent focused
- Left/right look counts
- Sleepy event counts
- Tab switch counts
- Lock mode violations

**Real-Time Alerts:**
- Repeated sleepy detection
- Repeated looking away
- Lock mode violations
- Configurable thresholds

### WebSocket Updates

Events are sent via WebSocket for real-time updates:
```javascript
{
  type: "attention_event",
  session_id: 1,
  attendance_id: 5,
  timestamp: "2025-11-19T10:30:00Z",
  labels: [
    { name: "focused", confidence: 0.92 },
    { name: "engaged", confidence: 0.85 }
  ],
  gaze: { yaw: -2.3, pitch: 1.5 },
  head_pose: { x: -1.8, y: 0.9, z: 0 },
  eyes_open_prob: 0.95
}
```

## 🔧 Advanced Topics

### Data Augmentation

```bash
python ml/augment.py \
  data/processed/synthetic_demo/metadata.jsonl \
  --out data/augmented/synthetic_demo \
  --copies 3
```

Augmentations applied:
- Brightness adjustment
- Gaussian noise
- Random occlusions
- Horizontal flip (with label adjustment)

### Calibration

User-specific calibration improves accuracy:

```javascript
// In student view
const calibration = await runCalibration();
// Stores yaw/pitch offsets in localStorage
```

### Active Learning

Queue low-confidence predictions for manual labeling:

```bash
python ml/active_learning.py \
  --events exported_events.jsonl \
  --threshold 0.45 \
  --out labeling_queue.jsonl
```

## 🐛 Troubleshooting

### Training Issues

**Out of Memory:**
```bash
# Reduce batch size
python ml/train.py --batch-size 16

# Use CPU mode
python ml/train.py --cpu
```

**Slow Training:**
```bash
# Use GPU
python ml/train.py  # Auto-detects GPU

# Enable mixed precision
python ml/train.py --mixed-precision
```

**Poor Accuracy:**
- Increase training data
- Train for more epochs
- Use real datasets instead of synthetic
- Add data augmentation
- Collect user-specific calibration data

### Export Issues

**Model Too Large:**
```bash
# Already quantized by default
# Check model size:
ls -lh frontend/public/models/focusmate-attention/tfjs/
```

**TF.js Conversion Fails:**
```bash
# Install tensorflowjs
pip install tensorflowjs

# Try without quantization
python ml/export_model.py --no-quantize
```

### Inference Issues

**Model Not Loading:**
- Check browser console for errors
- Verify model files exist
- Check file permissions
- System falls back to heuristics

**Low Accuracy:**
- Run calibration
- Check lighting conditions
- Verify webcam quality
- Train with more data

## 📚 Additional Resources

- **ML README:** `ml/README.md`
- **API Docs:** http://localhost:8000/docs
- **Testing Guide:** `docs/TESTING.md`
- **Features:** `docs/FEATURES.md`

## ✅ Acceptance Criteria

- [x] Model trained on unified datasets
- [x] Exports to TF.js/ONNX
- [x] Student webcam shows live labels
- [x] Teacher dashboard displays timeline
- [x] Stats and alerts within 5s
- [x] Tab-switch counts tracked
- [x] README with dataset sources
- [x] Training steps documented
- [x] Test/demo instructions provided

## 🎉 Success!

You now have a complete AI-powered attention detection system with:
- ✅ Multi-head model architecture
- ✅ Support for public datasets
- ✅ CPU and GPU training modes
- ✅ Model evaluation metrics
- ✅ Browser-based inference
- ✅ Real-time dashboard
- ✅ Comprehensive documentation

**Ready to train and deploy!** 🚀
