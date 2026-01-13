"""
Utility functions for simple gaze / engagement estimation.

NOTE: This is intentionally lightweight and rule-based. It uses
MediaPipe if available, but falls back to dummy heuristics for CI and testing.
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np

try:
    import cv2
    import mediapipe as mp
except Exception:  # pragma: no cover - optional deps during tests
    cv2 = None
    mp = None

EngagementState = Literal["ENGAGED", "PARTIAL", "NOT_ENGAGED"]


@dataclass
class EngagementResult:
    level: EngagementState
    faces_detected: int
    gaze_angle: float
    eyes_open: bool


def decode_base64_image(payload: str) -> Optional[np.ndarray]:
    """Decode a base64 image string into an OpenCV BGR frame."""

    try:
        data = base64.b64decode(payload)
        image = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(image, cv2.IMREAD_COLOR) if cv2 else None
        return frame
    except Exception:
        return None


def estimate_engagement(frame: np.ndarray | None) -> EngagementResult:
    """Return a simple engagement state from a frame."""

    if frame is None or cv2 is None or mp is None:
        # fallback heuristics
        return EngagementResult("PARTIAL", faces_detected=0, gaze_angle=0.0, eyes_open=True)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=2)
    result = face_mesh.process(rgb)
    face_mesh.close()

    faces = len(result.multi_face_landmarks or [])
    if faces == 0:
        return EngagementResult("NOT_ENGAGED", faces_detected=0, gaze_angle=0.0, eyes_open=False)

    # extremely simple: measure average x deviation of eyes vs center
    image_cols = frame.shape[1]
    total_angle = 0.0
    for face_landmarks in result.multi_face_landmarks:
        left_eye = face_landmarks.landmark[33]  # approx left eye
        right_eye = face_landmarks.landmark[263]
        center_x = (left_eye.x + right_eye.x) / 2
        deviation = abs(center_x - 0.5)  # 0 centered
        total_angle += deviation * 60  # convert to pseudo degrees

    gaze_angle = total_angle / faces

    if gaze_angle < 15:
        level: EngagementState = "ENGAGED"
    elif gaze_angle < 30:
        level = "PARTIAL"
    else:
        level = "NOT_ENGAGED"

    return EngagementResult(level, faces_detected=faces, gaze_angle=gaze_angle, eyes_open=True)


def summarize_frame(base64_frame: str | None) -> EngagementResult:
    """Helper for API endpoint that accepts base64 payload."""

    frame = decode_base64_image(base64_frame) if base64_frame else None
    return estimate_engagement(frame)

