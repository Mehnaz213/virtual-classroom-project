"""
MobileNetV3-based multi-head model for gaze/attention estimation.
"""

from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import layers, models


def build_model(
    input_shape: tuple[int, int, int] = (120, 160, 3),
    num_labels: int = 11,
) -> tf.keras.Model:
    base = tf.keras.applications.MobileNetV3Small(
        input_shape=input_shape,
        include_top=False,
        pooling="avg",
        weights=None,
    )

    x = base.output
    gaze_yaw = layers.Dense(64, activation="relu")(x)
    gaze_yaw = layers.Dense(1, name="gaze_yaw")(gaze_yaw)

    gaze_pitch = layers.Dense(64, activation="relu")(x)
    gaze_pitch = layers.Dense(1, name="gaze_pitch")(gaze_pitch)

    head_pose = layers.Dense(64, activation="relu")(x)
    head_pose_yaw = layers.Dense(1, name="head_yaw")(head_pose)
    head_pose_pitch = layers.Dense(1, name="head_pitch")(head_pose)

    eyes_open = layers.Dense(32, activation="relu")(x)
    eyes_open = layers.Dense(1, activation="sigmoid", name="eyes_open_prob")(eyes_open)

    label_logits = layers.Dense(128, activation="relu")(x)
    label_logits = layers.Dense(num_labels, activation="softmax", name="label_probs")(label_logits)

    model = models.Model(
        inputs=base.input,
        outputs=[gaze_yaw, gaze_pitch, head_pose_yaw, head_pose_pitch, eyes_open, label_logits],
    )
    losses = {
        "gaze_yaw": "mse",
        "gaze_pitch": "mse",
        "head_yaw": "mse",
        "head_pitch": "mse",
        "eyes_open_prob": "binary_crossentropy",
        "label_probs": "categorical_crossentropy",
    }
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=2e-4),
        loss=losses,
        metrics={
            "eyes_open_prob": ["accuracy"],
            "label_probs": ["accuracy"],
        },
    )
    return model


