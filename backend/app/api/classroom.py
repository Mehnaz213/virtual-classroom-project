from datetime import datetime
from secrets import token_hex
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import true
from sqlalchemy.orm import Session

from app.api import deps
from app.api.ws import schedule_broadcast
from app.db.session import get_db
from app.models import Attendance, ClassSession, EngagementEvent, EngagementLevel, User
from app.schemas import (
    ClassCreateRequest,
    DashboardResponse,
    JoinClassRequest,
    JoinResponse,
    LockModeRequest,
    SessionResponse,
    SessionSummary,
)
from app.services.dashboard import build_dashboard_payload

router = APIRouter(prefix="/class", tags=["classroom"])


@router.post("/create", response_model=SessionResponse)
def create_class(
    payload: ClassCreateRequest,
    teacher: User = Depends(deps.get_current_teacher),
    db: Session = Depends(get_db),
):
    code = token_hex(3).upper()
    new_session = ClassSession(topic=payload.topic, teacher_id=teacher.id, code=code)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/mine", response_model=List[SessionSummary])
def list_my_classes(
    teacher: User = Depends(deps.get_current_teacher),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timedelta
    
    # Only show sessions from the last 2 hours
    recent_time = datetime.utcnow() - timedelta(hours=2)
    
    sessions = (
        db.query(ClassSession)
        .filter(
            ClassSession.teacher_id == teacher.id,
            ClassSession.start_time >= recent_time
        )
        .order_by(ClassSession.start_time.desc())
        .all()
    )
    payload: List[SessionSummary] = []
    for session in sessions:
        attendee_count = (
            db.query(Attendance).filter(Attendance.session_id == session.id).count()
        )
        total_events = (
            db.query(EngagementEvent).filter(EngagementEvent.session_id == session.id).count()
        )
        engaged_events = (
            db.query(EngagementEvent)
            .filter(
                EngagementEvent.session_id == session.id,
                EngagementEvent.level == EngagementLevel.ENGAGED,
            )
            .count()
        )
        avg_engagement = (engaged_events / total_events) if total_events else 0.0
        payload.append(
            SessionSummary(
                id=session.id,
                code=session.code,
                topic=session.topic,
                teacher_id=session.teacher_id,
                start_time=session.start_time,
                is_live=session.is_live,
                attendee_count=attendee_count,
                avg_engagement=avg_engagement,
            )
        )
    return payload


@router.get("/code/{code}", response_model=SessionResponse)
def get_by_code(
    code: str,
    user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ClassSession)
        .filter(ClassSession.code == code.upper(), ClassSession.is_live.is_(True))
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not live")
    return session


@router.post("/{session_id}/join", response_model=JoinResponse)
def join_class(
    session_id: int,
    payload: JoinClassRequest,
    student: User = Depends(deps.get_current_student),
    db: Session = Depends(get_db),
):
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session or not session.is_live:
        raise HTTPException(status_code=404, detail="Session not available")
    if session.code != payload.code.upper():
        raise HTTPException(status_code=400, detail="Invalid session code")

    existing = (
        db.query(Attendance)
        .filter(Attendance.session_id == session.id, Attendance.student_id == student.id)
        .first()
    )
    if existing:
        existing.last_seen_at = datetime.utcnow()
        existing.lock_mode = payload.lock_mode
        db.commit()
        return JoinResponse(attendance_id=existing.id, session_code=session.code, lock_mode=existing.lock_mode)

    attendance = Attendance(
        session_id=session.id,
        student_id=student.id,
        lock_mode=payload.lock_mode,
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    schedule_broadcast(
        session.id,
        {
            "type": "attendance",
            "studentId": student.id,
            "action": "joined",
            "timestamp": attendance.joined_at.isoformat(),
        },
    )
    return JoinResponse(attendance_id=attendance.id, session_code=session.code, lock_mode=attendance.lock_mode)


@router.post("/{session_id}/lock", response_model=SessionResponse)
def toggle_lock_mode(
    session_id: int,
    payload: LockModeRequest,
    teacher: User = Depends(deps.get_current_teacher),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ClassSession)
        .filter(ClassSession.id == session_id, ClassSession.teacher_id == teacher.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    query = db.query(Attendance).filter(Attendance.session_id == session.id)
    if payload.student_id:
        query = query.filter(Attendance.student_id == payload.student_id)
    query.update({"lock_mode": payload.enabled})
    db.commit()
    schedule_broadcast(
        session.id,
        {
            "type": "lock_mode",
            "enabled": payload.enabled,
            "studentId": payload.student_id,
        },
    )
    return session


@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(
    session_id: int,
    teacher: User = Depends(deps.get_current_teacher),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ClassSession)
        .filter(ClassSession.id == session_id, ClassSession.teacher_id == teacher.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.is_live = False
    session.end_time = datetime.utcnow()
    db.commit()
    schedule_broadcast(
        session.id,
        {
            "type": "session_end",
            "timestamp": session.end_time.isoformat(),
        },
    )
    return session


@router.get("/{session_id}/dashboard", response_model=DashboardResponse)
def dashboard(
    session_id: int,
    teacher: User = Depends(deps.get_current_teacher),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ClassSession)
        .filter(ClassSession.id == session_id, ClassSession.teacher_id == teacher.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return build_dashboard_payload(db, session)

