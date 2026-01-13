# Focus Mate AI Dataset Documentation

## Overview

This document describes the dataset used to train the Focus Mate attention detection AI model.

---

## Dataset Information

### Dataset Name
**Synthetic Demo Dataset** (for development and testing)

### Location
- **Path**: `data/processed/synthetic_demo/`
- **Metadata**: `data/processed/synthetic_demo/metadata.jsonl`
- **Images**: `data/processed/synthetic_demo/frames/`

### Dataset Size
- Default: 1,000 samples
- Configurable via `--limit` parameter during generation

---

## Dataset Generation

### Generation Script
**File**: `ml/data_ingest.py`

### Command to Generate
```bash
python ml/data_ingest.py ingest synthetic_demo --limit 1000
```

### Generation Process
The synthetic dataset is generated programmatically using the `generate_synthetic_samples()` function in `ml/data_ingest.py` (lines 70-140).

For each sample:
1. Randomly selects an attention label
2. Generates realistic gaze angles based on the label
3. Creates corresponding head pose values
4. Assigns eye openness probability
5. Generates a synthetic image (160×120 RGB)
6. Saves metadata in JSONL format

---

## Attention Labels (11 Classes)

The dataset includes 11 distinct attention states:

| Label | Description | Typical Gaze Yaw | Typical Gaze Pitch | Eyes Open |
|-------|-------------|------------------|-------------------|-----------|
| `focused` | Looking directly at screen | 0° ± 2° | 0° ± 2° | 0.8-1.0 |
| `looking_left` | Gaze directed left | -15° ± 3° | 0° ± 2° | 0.7-1.0 |
| `looking_right` | Gaze directed right | +15° ± 3° | 0° ± 2° | 0.7-1.0 |
| `looking_up` | Gaze directed upward | 0° ± 2° | +10° ± 3° | 0.7-1.0 |
| `looking_down` | Gaze directed downward | 0° ± 2° | -10° ± 3° | 0.7-1.0 |
| `engaged` | Generally attentive | 0° ± 5° | 0° ± 5° | 0.7-1.0 |
| `partial_engaged` | Partially attentive | Variable | Variable | 0.7-1.0 |
| `sleepy` | Eyes closing, drowsy | 0° ± 5° | -5° ± 3° | 0.0-0.3 |
| `distracted_by_multi_face` | Multiple faces detected | Variable | Variable | 0.5-1.0 |
| `no_face` | No face detected | N/A | N/A | N/A |
| `unknown` | Uncertain state | Variable | Variable | 0.5-1.0 |

---

## Data Format

### Metadata Structure (JSONL)

Each line in `metadata.jsonl` contains one JSON object with the following fields:

```json
{
  "frame_path": "frames/synthetic_00000.jpg",
  "gaze_yaw": -15.76,
  "gaze_pitch": -4.40,
  "head_yaw": -6.96,
  "head_pitch": -1.15,
  "eyes_open_prob": 0.788,
  "label": "looking_left",
  "confidence": 0.789,
  "meta": {
    "source": "synthetic",
    "index": 0
  }
}
```

### Field Descriptions

| Field | Type | Description | Range |
|-------|------|-------------|-------|
| `frame_path` | string | Relative path to image file | - |
| `gaze_yaw` | float | Horizontal gaze angle (degrees) | -30° to +30° |
| `gaze_pitch` | float | Vertical gaze angle (degrees) | -20° to +20° |
| `head_yaw` | float | Horizontal head rotation (degrees) | -30° to +30° |
| `head_pitch` | float | Vertical head rotation (degrees) | -20° to +20° |
| `eyes_open_prob` | float | Probability eyes are open | 0.0 to 1.0 |
| `label` | string | Attention state classification | See labels above |
| `confidence` | float | Label confidence score | 0.7 to 0.95 |
| `meta` | object | Additional metadata | - |

---

## Sample Data Examples

### Example 1: Focused Student
```json
{
  "frame_path": "frames/synthetic_00001.jpg",
  "gaze_yaw": 2.51,
  "gaze_pitch": 4.10,
  "head_yaw": -5.49,
  "head_pitch": -5.07,
  "eyes_open_prob": 0.86,
  "label": "focused",
  "confidence": 0.71
}
```

### Example 2: Looking Left
```json
{
  "frame_path": "frames/synthetic_00000.jpg",
  "gaze_yaw": -15.76,
  "gaze_pitch": -4.40,
  "head_yaw": -6.96,
  "head_pitch": -1.15,
  "eyes_open_prob": 0.79,
  "label": "looking_left",
  "confidence": 0.79
}
```

### Example 3: Sleepy Student
```json
{
  "frame_path": "frames/synthetic_00042.jpg",
  "gaze_yaw": 1.23,
  "gaze_pitch": -6.45,
  "head_yaw": 2.11,
  "head_pitch": -7.89,
  "eyes_open_prob": 0.15,
  "label": "sleepy",
  "confidence": 0.88
}
```

---

## Files That Use This Dataset

### 1. Training Script
**File**: `ml/train.py`

**Usage**: Loads the dataset and trains the attention detection model

```python
# Load samples from metadata.jsonl
samples = load_samples(cfg.data_path)
train_samples, val_samples = train_val_split(samples)

# Preprocess for training
train_data = preprocess_samples(train_samples, cfg.image_size)
```

**Key Functions**:
- `load_samples()` - Reads metadata.jsonl
- `preprocess_samples()` - Converts to model-ready format
- `train_val_split()` - Splits into training/validation sets

### 2. Dataset Module
**File**: `ml/dataset.py`

**Usage**: Provides data loading and preprocessing utilities

### 3. Evaluation Script
**File**: `ml/eval.py`

**Usage**: Evaluates model performance on the dataset

### 4. Data Ingestion Script
**File**: `ml/data_ingest.py`

**Usage**: Generates and normalizes the dataset

**Key Function**: `generate_synthetic_samples(count, output_dir)`

---

## Training Process

### Step 1: Generate Dataset
```bash
python ml/data_ingest.py ingest synthetic_demo --limit 1000
```

### Step 2: Train Model
```bash
python ml/train.py \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --epochs 10 \
  --batch-size 32
```

### Step 3: Export Model
```bash
python ml/export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out frontend/public/models/focusmate-attention \
  --format tfjs
```

---

## Model Architecture

### Base Model
**MobileNetV3-Small** (lightweight, optimized for mobile/web)

### Input Specifications
- **Size**: 160×120 pixels
- **Format**: RGB (3 channels)
- **Normalization**: Pixel values divided by 255.0

### Output Heads (Multi-task Learning)

1. **Gaze Yaw** - Horizontal gaze angle
2. **Gaze Pitch** - Vertical gaze angle
3. **Head Yaw** - Horizontal head rotation
4. **Head Pitch** - Vertical head rotation
5. **Eyes Open Probability** - Eye openness score
6. **Label Probabilities** - 11-class attention classification

### Model Size
- **Uncompressed**: ~10MB
- **Quantized**: <5MB
- **Format**: TensorFlow.js (for browser deployment)

---

## Alternative Datasets (Production Use)

For production deployment, the following public datasets are recommended:

### 1. GazeCapture (MIT)
- **URL**: https://gazecapture.csail.mit.edu/
- **License**: Research-only (request access)
- **Size**: 2.5M frames from 1,474 subjects
- **Notes**: Mobile-focused, on-screen vs off-screen attention

### 2. MPIIGaze
- **URL**: https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/gaze-estimation/mpiigaze
- **License**: Non-commercial (request access)
- **Size**: 213,659 images from 15 subjects
- **Notes**: Laptop gaze with head-pose diversity

### 3. Columbia Gaze
- **URL**: http://www.cs.columbia.edu/CAVE/databases/columbia_gaze/
- **License**: Non-commercial (direct download)
- **Size**: 5,880 images from 56 subjects
- **Notes**: Discrete left/right/up/down gaze samples

### 4. ETH-XGaze
- **URL**: https://ait.ethz.ch/projects/2020/xgaze/
- **License**: Research-only (request access)
- **Size**: 1M+ images from 110 subjects
- **Notes**: Large multi-view head-pose dataset

### 5. OpenEDS (Facebook/Meta)
- **URL**: https://research.fb.com/openeds-2020-challenge/
- **License**: CC BY-NC 4.0 (registration required)
- **Size**: 12,759 sequences
- **Notes**: Eye segmentation and eye-openness cues

---

## Dataset Statistics

### Label Distribution (Synthetic Dataset)
The synthetic dataset generates approximately equal distribution across all 11 labels:
- Each label: ~9% of total samples
- Ensures balanced training across all attention states

### Angle Distributions

**Gaze Angles**:
- Yaw range: -30° to +30°
- Pitch range: -20° to +20°
- Gaussian distribution around label-specific means

**Head Pose**:
- Yaw range: -30° to +30°
- Pitch range: -25° to +25°
- Correlated with gaze direction but with added variance

**Eye Openness**:
- Focused/Engaged: 0.7-1.0
- Sleepy: 0.0-0.3
- Other states: 0.5-1.0

---

## Configuration

### Training Configuration
**File**: `ml/config.py`

```python
@dataclass
class TrainingConfig:
    data_path: Path
    output_dir: Path = Path("artifacts/model")
    epochs: int = 5
    batch_size: int = 32
    learning_rate: float = 2e-4
    image_size: tuple[int, int] = (120, 160)
    label_smoothing: float = 0.05
    num_workers: int = 4
```

---

## Quality Assurance

### Data Validation
- All gaze/head angles within realistic ranges
- Eye openness probabilities between 0.0 and 1.0
- Confidence scores between 0.7 and 0.95
- All image files exist and are readable

### Label Consistency
- Gaze angles match expected ranges for each label
- Eye openness appropriate for attention state
- Head pose correlated with gaze direction

---

## Future Enhancements

### Planned Improvements
1. **Real Data Collection**: Implement local calibration capture tool
2. **Public Dataset Integration**: Add adapters for GazeCapture, MPIIGaze, etc.
3. **Data Augmentation**: Add rotation, brightness, blur variations
4. **Active Learning**: Collect and label edge cases from production
5. **Multi-face Support**: Enhanced distraction detection

### Adapter Implementation
To add support for public datasets, implement in `ml/data_ingest.py`:
1. Parse dataset-specific format
2. Extract gaze angles, head pose, eye openness
3. Map to Focus Mate attention labels
4. Write to unified JSONL format

---

## References

### Code Files
- `ml/data_ingest.py` - Dataset generation and ingestion
- `ml/train.py` - Model training pipeline
- `ml/dataset.py` - Data loading utilities
- `ml/config.py` - Training configuration
- `ml/labels.py` - Label definitions and mappings

### Documentation
- `ml/README.md` - ML pipeline overview
- `docs/FEATURES.md` - Complete feature documentation
- `TRAINING_GUIDE.md` - Step-by-step training guide

---

## Contact & Support

For questions about the dataset or training process:
1. Review the documentation in `ml/README.md`
2. Check the training guide in `TRAINING_GUIDE.md`
3. Examine the code in `ml/data_ingest.py`

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Project**: Focus Mate Virtual Classroom
