from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models import EngagementEvent, User
from app.schemas import LabelConfidence, TimelinePoint

router = APIRouter(prefix="/labeler", tags=["labeler"])


@router.get("/queue")
def review_queue(
    teacher: User = Depends(deps.get_current_teacher),
    db: Session = Depends(get_db),
):
    events = (
        db.query(EngagementEvent)
        .join(EngagementEvent.attendance)
        .join(EngagementEvent.session)
        .filter(
            EngagementEvent.labels != None,  # noqa: E711
            EngagementEvent.session.has(teacher_id=teacher.id),
        )
        .order_by(EngagementEvent.timestamp.desc())
        .limit(150)
        .all()
    )
    payload = []
    for event in events:
        labels = event.labels or []
        label_objs = [
            LabelConfidence(name=label.get("name"), confidence=float(label.get("confidence", 0)))
            for label in labels
            if isinstance(label, dict) and label.get("name")
        ]
        payload.append(
            {
                "timestamp": event.timestamp.isoformat(),
                "student_name": event.attendance.student.full_name,
                "attendance_id": event.attendance_id,
                "level": event.level,
                "tab_switch": event.tab_switch,
                "multiple_faces": event.multiple_faces,
                "labels": [label.dict() for label in label_objs],
                "meta": {
                    "frame_url": event.meta.get("frame_url") if isinstance(event.meta, dict) else None,
                },
            }
        )
    return payload


