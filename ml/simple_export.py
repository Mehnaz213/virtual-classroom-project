"""Simple TF.js export without tensorflow-decision-forests dependency"""
import tensorflow as tf
from pathlib import Path
import sys

# Load the model
model_path = sys.argv[1] if len(sys.argv) > 1 else "artifacts/focusmate_model/saved_model"
output_path = sys.argv[2] if len(sys.argv) > 2 else "frontend/public/models/focusmate-attention"

print(f"Loading model from {model_path}...")
model = tf.keras.models.load_model(model_path)

print(f"Saving to {output_path}...")
Path(output_path).mkdir(parents=True, exist_ok=True)

# Save as TF.js layers model format
model.save(output_path, save_format='tf')

print(f"✓ Model exported to {output_path}")
print("Note: You'll need to convert this to TF.js format manually or use the model directly")
