from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models import Attendance, ClassSession, EngagementEvent, EngagementLevel, TabSwitchEventLog
from app.schemas import (
    AttendanceResponse,
    DashboardResponse,
    LabelBreakdown,
    LabelConfidence,
    TimelinePoint,
)


def _event_labels(event: EngagementEvent) -> List[LabelConfidence]:
    records = event.labels or (event.meta or {}).get("labels") or []
    payload = []
    for record in records:
        name = record.get("name") if isinstance(record, dict) else record.name  # type: ignore[attr-defined]
        confidence = record.get("confidence") if isinstance(record, dict) else record.confidence  # type: ignore[attr-defined]
        if name is None:
            continue
        payload.append(LabelConfidence(name=name, confidence=float(confidence or 0)))
    return payload


def build_dashboard_payload(
    db: Session,
    session: ClassSession,
    lookback_minutes: int = 30,
) -> DashboardResponse:
    attendance_rows: List[Attendance] = (
        db.query(Attendance)
        .filter(Attendance.session_id == session.id)
        .order_by(Attendance.last_seen_at.desc())
        .all()
    )

    attendance_payload: List[AttendanceResponse] = []
    tab_switch_alerts: List[str] = []
    sleepy_alerts: List[str] = []
    lock_violations: List[str] = []
    engaged = 0
    label_counter: Dict[str, int] = {}

    for row in attendance_rows:
        last_event = (
            db.query(EngagementEvent)
            .filter(EngagementEvent.attendance_id == row.id)
            .order_by(EngagementEvent.timestamp.desc())
            .first()
        )
        level = last_event.level if last_event else EngagementLevel.PARTIAL
        if level == EngagementLevel.ENGAGED:
            engaged += 1
        if last_event:
            if last_event.tab_switch:
                tab_switch_alerts.append(
                    f"{row.student.full_name} switched tabs at {last_event.timestamp.isoformat()}",
                )
            labels = _event_labels(last_event)
            for label in labels:
                label_counter[label.name] = label_counter.get(label.name, 0) + 1
                if label.name == "sleepy" and label.confidence > 0.5:
                    sleepy_alerts.append(
                        f"{row.student.full_name} sleepy @ {last_event.timestamp.isoformat()}"
                    )
        
        # Check for lock mode violations
        violation_count = (
            db.query(TabSwitchEventLog)
            .filter(
                TabSwitchEventLog.attendance_id == row.id,
                TabSwitchEventLog.lock_mode_violation == True,
            )
            .count()
        )
        if violation_count > 0:
            lock_violations.append(
                f"{row.student.full_name} has {violation_count} lock mode violations"
            )

        attendance_payload.append(
            AttendanceResponse(
                attendance_id=row.id,
                student_id=row.student_id,
                student_name=row.student.full_name,
                last_seen_at=row.last_seen_at,
                lock_mode=row.lock_mode,
                latest_level=level,
            )
        )

    cutoff = datetime.utcnow() - timedelta(minutes=lookback_minutes)
    events = (
        db.query(EngagementEvent)
        .filter(EngagementEvent.session_id == session.id, EngagementEvent.timestamp >= cutoff)
        .order_by(EngagementEvent.timestamp.desc())
        .limit(250)
        .all()
    )

    timeline = [
        TimelinePoint(
            timestamp=event.timestamp,
            student_name=event.attendance.student.full_name,
            level=event.level,
            tab_switch=event.tab_switch,
            multiple_faces=event.multiple_faces,
            labels=_event_labels(event),
        )
        for event in events
    ]

    engagement_ratio = (engaged / len(attendance_rows)) if attendance_rows else 0.0
    total_labels = sum(label_counter.values()) or 1
    label_breakdown = [
        LabelBreakdown(
            name=name,
            count=count,
            percentage=round(count / total_labels * 100, 2),
        )
        for name, count in sorted(label_counter.items(), key=lambda item: item[1], reverse=True)
    ]

    return DashboardResponse(
        session_id=session.id,
        topic=session.topic,
        is_live=session.is_live,
        start_time=session.start_time,
        attendance=attendance_payload,
        engagement_ratio=engagement_ratio,
        tab_switch_alerts=tab_switch_alerts,
        timeline=timeline,
        label_breakdown=label_breakdown,
        sleepy_alerts=sleepy_alerts,
        lock_violations=lock_violations,
    )

