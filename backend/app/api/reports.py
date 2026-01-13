import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models import Attendance, ClassSession, EngagementEvent, EngagementLevel, User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{session_id}")
def download_report(
    session_id: int,
    format: str = "csv",
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

    rows = (
        db.query(Attendance)
        .filter(Attendance.session_id == session_id)
        .all()
    )

    records = []
    for row in rows:
        total_events = (
            db.query(EngagementEvent)
            .filter(EngagementEvent.attendance_id == row.id)
            .count()
        )
        engaged_events = (
            db.query(EngagementEvent)
            .filter(
                EngagementEvent.attendance_id == row.id,
                EngagementEvent.level == EngagementLevel.ENGAGED,
            )
            .count()
        )
        percent = (engaged_events / total_events * 100) if total_events else 0.0
        records.append(
            {
                "student": row.student.full_name,
                "joined_at": row.joined_at.isoformat(),
                "last_seen_at": row.last_seen_at.isoformat(),
                "engagement_percent": round(percent, 2),
            }
        )

    if format == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=records[0].keys() if records else [])
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
        return Response(
            content=buffer.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=session-{session_id}.csv"},
        )
    elif format == "pdf":
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="PDF generation libraries missing. Use CSV instead.",
            )

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        textobject = c.beginText(40, 750)
        textobject.textLine(f"Session Report #{session.id} - {session.topic}")
        textobject.textLine(f"Generated at {datetime.utcnow().isoformat()}")
        textobject.textLine("")
        for rec in records:
            textobject.textLine(
                f"{rec['student']}: engagement {rec['engagement_percent']}%, last seen {rec['last_seen_at']}"
            )
        c.drawText(textobject)
        c.showPage()
        c.save()
        buffer.seek(0)
        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=session-{session_id}.pdf"},
        )
    else:
        raise HTTPException(status_code=400, detail="format must be csv or pdf")

