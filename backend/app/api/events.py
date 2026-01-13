from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.api.ws import schedule_broadcast
from app.core import engagement
from app.core.labels import derive_attention_labels
from app.db.session import get_db
from app.models import (
    Attendance,
    EngagementEvent,
    EngagementLevel,
    TabSwitchEventLog,
    User,
)
from app.schemas import FrameEvent, TabSwitchEvent

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/frame")
def post_frame(
    payload: FrameEvent,
    user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
):
    attendance = (
        db.query(Attendance)
        .filter(Attendance.id == payload.attendance_id)
        .first()
    )
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    if attendance.student_id != user.id and attendance.session.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this event")

    result = engagement.summarize_frame(payload.frame_b64) if payload.client_level is None else None
    level = payload.client_level or EngagementLevel[result.level]
    labels = payload.labels

    def _normalize(entries):
        normalized = []
        for entry in entries or []:
            if isinstance(entry, dict):
                normalized.append(entry)
            else:
                normalized.append(entry.dict())
        return normalized

    if labels is None:
        labels = derive_attention_labels(
            gaze_yaw=payload.gaze.yaw if payload.gaze else None,
            gaze_pitch=payload.gaze.pitch if payload.gaze else None,
            head_yaw=payload.head_pose.x if payload.head_pose else None,
            head_pitch=payload.head_pose.y if payload.head_pose else None,
            eyes_open_prob=payload.attention_score,
            face_present=payload.face_present if payload.face_present is not None else True,
            multi_face=payload.multiple_faces,
            base_confidence=payload.confidence or 0.6,
        )
    labels = _normalize(labels)
    gaze_data = payload.gaze.dict() if payload.gaze else {}
    head_pose_data = payload.head_pose.dict() if payload.head_pose else {}
    event = EngagementEvent(
        session_id=payload.session_id,
        attendance_id=attendance.id,
        level=level,
        meta={
            "gaze_angle": result.gaze_angle if result else None,
            "faces": result.faces_detected if result else None,
            "attention_score": payload.attention_score,
            "reason": payload.reason,
        },
        tab_switch=payload.tab_switch,
        multiple_faces=payload.multiple_faces,
        labels=labels,
        gaze=gaze_data,
        head_pose=head_pose_data,
        confidence=str(payload.confidence or payload.attention_score or 0.0),
    )
    db.add(event)
    attendance.last_seen_at = datetime.utcnow()
    db.commit()
    schedule_broadcast(
        payload.session_id,
        {
            "type": "event",
            "level": level.value,
            "tabSwitch": payload.tab_switch,
            "attendanceId": attendance.id,
            "studentId": attendance.student_id,
            "timestamp": event.timestamp.isoformat(),
            "labels": labels,
        },
    )
    return {"status": "ok", "level": level.value}


@router.post("/tab-switch")
def tab_switch_event(
    payload: TabSwitchEvent,
    user: User = Depends(deps.get_current_student),
    db: Session = Depends(get_db),
):
    attendance = (
        db.query(Attendance)
        .filter(Attendance.id == payload.attendance_id, Attendance.session_id == payload.session_id)
        .first()
    )
    if not attendance or attendance.student_id != user.id:
        raise HTTPException(status_code=404, detail="Attendance not found")

    level = EngagementLevel.PARTIAL if payload.tab_visible else EngagementLevel.NOT_ENGAGED
    event = EngagementEvent(
        session_id=payload.session_id,
        attendance_id=attendance.id,
        level=level,
        tab_switch=not payload.tab_visible if payload.tab_visible is not None else True,
        meta={"note": payload.note},
    )
    db.add(event)

    log = TabSwitchEventLog(
        session_id=payload.session_id,
        attendance_id=attendance.id,
        event_type=payload.event_type,
        timestamp=payload.timestamp or datetime.utcnow(),
        tab_count=payload.tab_count or 0,
        tab_visible=payload.tab_visible if payload.tab_visible is not None else False,
        lock_mode_active=payload.lock_mode_active or False,
        lock_mode_violation=payload.lock_mode_violation or False,
        meta=payload.meta or {},
    )
    db.add(log)

    attendance.last_seen_at = datetime.utcnow()
    db.commit()
    schedule_broadcast(
        payload.session_id,
        {
            "type": "tab_switch",
            "level": level.value,
            "tabVisible": payload.tab_visible,
            "attendanceId": attendance.id,
            "studentId": attendance.student_id,
            "timestamp": log.timestamp.isoformat(),
            "tabCount": log.tab_count,
            "lockModeActive": log.lock_mode_active,
            "lockModeViolation": log.lock_mode_violation,
        },
    )
    return {"status": "ok"}

