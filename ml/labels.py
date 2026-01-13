"""
Label taxonomy and mapping utilities.
"""

from __future__ import annotations

from typing import Dict, List

LABELS = [
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
]
LABEL_TO_INDEX: Dict[str, int] = {label: idx for idx, label in enumerate(LABELS)}


def label_from_outputs(
    gaze_yaw: float,
    gaze_pitch: float,
    eyes_open_prob: float,
    multiple_faces: bool,
    confidence: float,
) -> str:
    if multiple_faces:
        return "distracted_by_multi_face"
    if confidence < 0.3:
        return "unknown"
    if eyes_open_prob < 0.2:
        return "sleepy"
    if abs(gaze_yaw) < 5 and abs(gaze_pitch) < 5:
        return "focused"
    if abs(gaze_yaw) < 8 and abs(gaze_pitch) < 8:
        return "engaged"
    if gaze_yaw <= -8:
        return "looking_left"
    if gaze_yaw >= 8:
        return "looking_right"
    if gaze_pitch >= 6:
        return "looking_up"
    if gaze_pitch <= -6:
        return "looking_down"
    return "partial_engaged"


def one_hot(label: str) -> List[float]:
    vec = [0.0] * len(LABELS)
    vec[LABEL_TO_INDEX.get(label, LABEL_TO_INDEX["unknown"])] = 1.0
    return vec


