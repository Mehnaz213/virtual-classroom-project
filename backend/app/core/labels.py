from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LabelConfig:
    name: str
    threshold: float


LABEL_CONFIDENCE_FLOOR = 0.15


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(value, upper))


def _direction_from_angle(angle: float, positive_label: str, negative_label: str, confidence: float) -> Optional[dict]:
    abs_angle = abs(angle)
    if abs_angle < 8:
        return None
    label = positive_label if angle > 0 else negative_label
    score = _clamp(confidence * min(1.0, abs_angle / 45.0))
    if score < LABEL_CONFIDENCE_FLOOR:
        return None
    return {"name": label, "confidence": round(score, 3)}


def derive_attention_labels(
    gaze_yaw: Optional[float],
    gaze_pitch: Optional[float],
    head_yaw: Optional[float],
    head_pitch: Optional[float],
    eyes_open_prob: Optional[float],
    face_present: bool,
    multi_face: bool,
    base_confidence: float = 0.6,
) -> List[dict]:
    """
    Map raw gaze/head pose values into discrete Focus Mate attention labels.
    This is intentionally heuristic so tests can validate deterministic output.
    """

    labels: List[dict] = []
    confidence = _clamp(base_confidence)

    if not face_present:
        labels.append({"name": "no_face", "confidence": 0.9})
        return labels

    if multi_face:
        labels.append({"name": "distracted_by_multi_face", "confidence": max(confidence, 0.6)})

    if eyes_open_prob is not None and eyes_open_prob < 0.35:
        labels.append({"name": "sleepy", "confidence": _clamp(1 - eyes_open_prob)})

    if gaze_yaw is not None:
        direction = _direction_from_angle(gaze_yaw, "looking_right", "looking_left", confidence)
        if direction:
            labels.append(direction)

    if gaze_pitch is not None:
        direction = _direction_from_angle(gaze_pitch, "looking_up", "looking_down", confidence)
        if direction:
            labels.append(direction)

    engaged_conf = confidence
    if not labels:
        engaged_conf = max(0.75, confidence)
        labels.append({"name": "focused", "confidence": engaged_conf})
        labels.append({"name": "engaged", "confidence": engaged_conf})
    else:
        labels.append({"name": "partial_engaged", "confidence": confidence})

    if base_confidence < 0.3:
        labels.append({"name": "unknown", "confidence": 0.3})

    # Deduplicate by label name, keep highest confidence
    dedup = {}
    for entry in labels:
        existing = dedup.get(entry["name"])
        if not existing or existing["confidence"] < entry["confidence"]:
            dedup[entry["name"]] = entry

    return list(dedup.values())


