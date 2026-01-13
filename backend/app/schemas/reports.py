from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.models.session import EngagementLevel


class ReportRow(BaseModel):
    student_name: str
    joined_at: datetime
    last_seen_at: datetime
    engagement_percent: float


class ReportResponse(BaseModel):
    session_id: int
    topic: str
    rows: List[ReportRow]

