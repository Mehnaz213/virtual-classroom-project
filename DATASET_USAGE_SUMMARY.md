# Dataset Usage Summary

## Quick Answer

**Dataset Used**: Synthetic Demo Dataset (generated programmatically)  
**Location**: `data/processed/synthetic_demo/metadata.jsonl`  
**Size**: 1,000 samples (configurable)

---

## Files That Use the Dataset

### 1. **ml/data_ingest.py** (GENERATES THE DATASET)
- **Function**: `generate_synthetic_samples(count, output_dir)`
- **Lines**: 70-140
- **Purpose**: Creates synthetic training data with realistic gaze angles and attention labels
- **Output**: 
  - `data/processed/synthetic_demo/metadata.jsonl` (metadata)
  - `data/processed/synthetic_demo/frames/*.jpg` (images)

### 2. **ml/train.py** (TRAINS THE MODEL)
- **Function**: `main()`
- **Lines**: 60-120
- **Purpose**: Loads dataset and trains the attention detection model
- **Key Operations**:
  ```python
  samples = load_samples(cfg.data_path)  # Reads metadata.jsonl
  train_samples, val_samples = train_val_split(samples)
  train_data = preprocess_samples(train_samples, cfg.image_size)
  model.fit(train_data["images"], train_data["targets"], ...)
  ```

### 3. **ml/dataset.py** (LOADS AND PROCESSES DATA)
- **Functions**: 
  - `load_samples(metadata_path)` - Reads JSONL file
  - `train_val_split(samples)` - Splits into train/validation
  - `preprocess_samples(samples)` - Converts to model format
- **Purpose**: Provides data loading utilities for training

### 4. **ml/eval.py** (EVALUATES MODEL)
- **Purpose**: Tests model performance on validation dataset
- **Uses**: Same dataset loading functions from `ml/dataset.py`

---

## How to Generate the Dataset

```bash
# Generate 1000 synthetic samples
python ml/data_ingest.py ingest synthetic_demo --limit 1000

# Output:
# - data/processed/synthetic_demo/metadata.jsonl
# - data/processed/synthetic_demo/frames/synthetic_00000.jpg
# - data/processed/synthetic_demo/frames/synthetic_00001.jpg
# - ... (1000 images total)
```

---

## How to Train with the Dataset

```bash
# Train model using the generated dataset
python ml/train.py \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --epochs 10 \
  --batch-size 32

# Output:
# - artifacts/focusmate_model/saved_model/ (trained model)
# - artifacts/focusmate_model/checkpoints/ (training checkpoints)
# - artifacts/focusmate_model/logs/ (TensorBoard logs)
```

---

## Dataset Format

Each line in `metadata.jsonl`:
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
  "meta": {"source": "synthetic", "index": 0}
}
```

---

## 11 Attention Labels

1. `focused` - Looking at screen
2. `looking_left` - Gaze directed left
3. `looking_right` - Gaze directed right
4. `looking_up` - Gaze directed upward
5. `looking_down` - Gaze directed downward
6. `engaged` - Generally attentive
7. `partial_engaged` - Partially attentive
8. `sleepy` - Eyes closing
9. `distracted_by_multi_face` - Multiple faces
10. `no_face` - No face detected
11. `unknown` - Uncertain state

---

## Complete Training Pipeline

```bash
# Step 1: Generate dataset
python ml/data_ingest.py ingest synthetic_demo --limit 1000

# Step 2: Train model
python ml/train.py --data data/processed/synthetic_demo/metadata.jsonl --epochs 10

# Step 3: Export for browser
python ml/export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out frontend/public/models/focusmate-attention \
  --format tfjs
```

---

## For PDF Conversion

To convert this documentation to PDF, use one of these methods:

### Method 1: Using Pandoc
```bash
pandoc DATASET_DOCUMENTATION.md -o DATASET_DOCUMENTATION.pdf
```

### Method 2: Using Markdown to PDF Online
1. Open https://www.markdowntopdf.com/
2. Upload `DATASET_DOCUMENTATION.md`
3. Download the PDF

### Method 3: Using VS Code Extension
1. Install "Markdown PDF" extension
2. Open `DATASET_DOCUMENTATION.md`
3. Right-click → "Markdown PDF: Export (pdf)"
