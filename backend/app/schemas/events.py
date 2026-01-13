from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from app.models.session import EngagementLevel


class LabelConfidence(BaseModel):
    name: str
    confidence: float


class GazeVector(BaseModel):
    yaw: float = 0.0
    pitch: float = 0.0


class HeadPose(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class FrameEvent(BaseModel):
    session_id: int
    attendance_id: int
    frame_b64: Optional[str] = None
    tab_switch: bool = False
    multiple_faces: bool = False
    client_level: Optional[EngagementLevel] = None
    attention_score: Optional[float] = None
    reason: Optional[str] = None
    labels: Optional[List[LabelConfidence]] = None
    gaze: Optional[GazeVector] = None
    head_pose: Optional[HeadPose] = None
    face_present: Optional[bool] = None
    confidence: Optional[float] = None
    eyes_open_prob: Optional[float] = None
    gaze_yaw: Optional[float] = None
    gaze_pitch: Optional[float] = None
    head_yaw: Optional[float] = None
    head_pitch: Optional[float] = None


class TabSwitchEvent(BaseModel):
    session_id: int
    attendance_id: int
    tab_visible: Optional[bool] = None
    event_type: str = "tab_switch"
    timestamp: Optional[datetime] = None
    tab_count: Optional[int] = None
    meta: Optional[Any] = None
    note: Optional[str] = None
    lock_mode_active: Optional[bool] = False
    lock_mode_violation: Optional[bool] = False


class EventResponse(BaseModel):
    timestamp: datetime
    level: EngagementLevel
    meta: Any
    tab_switch: bool
    multiple_faces: bool

