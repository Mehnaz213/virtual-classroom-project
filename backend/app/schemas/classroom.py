from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.session import EngagementLevel


class ClassCreateRequest(BaseModel):
    topic: str


class JoinClassRequest(BaseModel):
    code: str
    lock_mode: bool = False


class JoinResponse(BaseModel):
    attendance_id: int
    session_code: str
    lock_mode: bool


class LockModeRequest(BaseModel):
    enabled: bool
    student_id: Optional[int] = None


class AttendanceResponse(BaseModel):
    attendance_id: int
    student_id: int
    student_name: str
    last_seen_at: datetime
    lock_mode: bool
    latest_level: EngagementLevel


class LabelConfidence(BaseModel):
    name: str
    confidence: float


class TimelinePoint(BaseModel):
    timestamp: datetime
    student_name: str
    level: EngagementLevel
    tab_switch: bool
    multiple_faces: bool
    labels: List[LabelConfidence] = []


class LabelBreakdown(BaseModel):
    name: str
    count: int
    percentage: float


class DashboardResponse(BaseModel):
    session_id: int
    topic: str
    is_live: bool
    start_time: datetime
    attendance: List[AttendanceResponse]
    engagement_ratio: float
    tab_switch_alerts: List[str]
    timeline: List[TimelinePoint]
    label_breakdown: List[LabelBreakdown]
    sleepy_alerts: List[str]
    lock_violations: List[str] = []


class SessionResponse(BaseModel):
    id: int
    code: str
    topic: str
    teacher_id: int
    start_time: datetime
    is_live: bool

    class Config:
        orm_mode = True


class SessionSummary(SessionResponse):
    attendee_count: int
    avg_engagement: float

