from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import Attendance, ClassSession, EngagementEvent, EngagementLevel, User, UserRole


def init_db(db: Session):
    """Seed default teacher and students for demos."""

    if db.query(User).count() > 0:
        return

    teacher = User(
        email="john.teacher@school.edu",
        full_name="John Smith",
        role=UserRole.TEACHER,
        hashed_password=get_password_hash("SecurePass123!"),
    )
    student_a = User(
        email="alice.student@school.edu",
        full_name="Alice Johnson",
        role=UserRole.STUDENT,
        hashed_password=get_password_hash("StudentPass123!"),
    )
    student_b = User(
        email="bob.student@school.edu",
        full_name="Bob Wilson",
        role=UserRole.STUDENT,
        hashed_password=get_password_hash("StudentPass123!"),
    )

    session = ClassSession(code="CS101", topic="Introduction to Programming", teacher=teacher)
    attendance_a = Attendance(session=session, student=student_a, lock_mode=False)
    attendance_b = Attendance(session=session, student=student_b, lock_mode=False)

    now = datetime.utcnow()
    for idx in range(5):
        db.add(
            EngagementEvent(
                session=session,
                attendance=attendance_a if idx % 2 == 0 else attendance_b,
                timestamp=now - timedelta(minutes=5 - idx),
                level=EngagementLevel.ENGAGED if idx % 3 else EngagementLevel.PARTIAL,
                meta={"gaze": "center"},
            )
        )

    db.add_all([teacher, student_a, student_b, session, attendance_a, attendance_b])
    db.commit()

