from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.user import User


class EngagementLevel(str, PyEnum):
    ENGAGED = "ENGAGED"
    PARTIAL = "PARTIAL"
    NOT_ENGAGED = "NOT_ENGAGED"


class ClassSession(Base):
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    topic = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_live = Column(Boolean, default=True)

    teacher = relationship("User", back_populates="classes")
    attendance = relationship("Attendance", back_populates="session")
    events = relationship("EngagementEvent", back_populates="session")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    lock_mode = Column(Boolean, default=False)

    session = relationship("ClassSession", back_populates="attendance")
    student = relationship("User", back_populates="attendance")
    events = relationship("EngagementEvent", back_populates="attendance")


class EngagementEvent(Base):
    __tablename__ = "engagement_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
    attendance_id = Column(Integer, ForeignKey("attendance.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(Enum(EngagementLevel), default=EngagementLevel.ENGAGED)
    meta = Column(JSON, default=dict)
    tab_switch = Column(Boolean, default=False)
    multiple_faces = Column(Boolean, default=False)
    labels = Column(JSON, default=list)
    gaze = Column(JSON, default=dict)
    head_pose = Column(JSON, default=dict)
    confidence = Column(String, default="0.0")

    session = relationship("ClassSession", back_populates="events")
    attendance = relationship("Attendance", back_populates="events")


class TabSwitchEventLog(Base):
    __tablename__ = "tab_switch_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
    attendance_id = Column(Integer, ForeignKey("attendance.id"), nullable=False)
    event_type = Column(String, default="tab_switch", nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    tab_count = Column(Integer, default=0)
    tab_visible = Column(Boolean, default=True)
    lock_mode_active = Column(Boolean, default=False)
    lock_mode_violation = Column(Boolean, default=False)
    meta = Column(JSON, default=dict)

