#!/usr/bin/env python3
"""
Focus Mate - Test Data Generator

Generates synthetic test data for development and testing:
- Sample users (teachers and students)
- Class sessions
- Attendance records
- Engagement events with all 11 attention labels
- Tab switch events with lock mode violations
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path and change to backend directory
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
import os
os.chdir(str(backend_dir))

from app.db.session import SessionLocal
from app.models import (
    Attendance,
    ClassSession,
    EngagementEvent,
    EngagementLevel,
    TabSwitchEventLog,
    User,
)
from app.core.security import get_password_hash

ATTENTION_LABELS = [
    "focused",
    "looking_left",
    "looking_right",
    "looking_up",
    "looking_down",
    "engaged",
    "partial_engaged",
    "sleepy",
    "distracted_by_multi_face",
    "no_face",
    "unknown",
]


def create_users(db):
    """Create sample users."""
    print("Creating users...")
    
    # Teacher
    teacher = User(
        email="demo.teacher@focusmate.com",
        full_name="Demo Teacher",
        role="teacher",
        hashed_password=get_password_hash("teacher123"),
    )
    db.add(teacher)
    
    # Students
    students = []
    for i in range(1, 6):
        student = User(
            email=f"demo.student{i}@focusmate.com",
            full_name=f"Demo Student {i}",
            role="student",
            hashed_password=get_password_hash("student123"),
        )
        db.add(student)
        students.append(student)
    
    db.commit()
    print(f"✓ Created 1 teacher and {len(students)} students")
    return teacher, students


def create_session(db, teacher):
    """Create a sample class session."""
    print("Creating class session...")
    
    session = ClassSession(
        code="DEMO01",
        topic="Focus Mate Demo Session",
        teacher_id=teacher.id,
        start_time=datetime.utcnow() - timedelta(hours=1),
        is_live=True,
    )
    db.add(session)
    db.commit()
    
    print(f"✓ Created session: {session.topic} (code: {session.code})")
    return session


def create_attendance(db, session, students):
    """Create attendance records."""
    print("Creating attendance records...")
    
    attendance_records = []
    for i, student in enumerate(students):
        # Some students have lock mode enabled
        lock_mode = i % 2 == 0
        
        attendance = Attendance(
            session_id=session.id,
            student_id=student.id,
            joined_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 50)),
            last_seen_at=datetime.utcnow() - timedelta(seconds=random.randint(0, 60)),
            lock_mode=lock_mode,
        )
        db.add(attendance)
        attendance_records.append(attendance)
    
    db.commit()
    print(f"✓ Created {len(attendance_records)} attendance records")
    return attendance_records


def create_engagement_events(db, session, attendance_records, count=100):
    """Create engagement events with varied attention labels."""
    print(f"Creating {count} engagement events...")
    
    events = []
    for _ in range(count):
        attendance = random.choice(attendance_records)
        
        # Select random label with weighted distribution
        label_weights = {
            "focused": 0.25,
            "engaged": 0.20,
            "partial_engaged": 0.15,
            "looking_left": 0.08,
            "looking_right": 0.08,
            "looking_up": 0.05,
            "looking_down": 0.05,
            "sleepy": 0.05,
            "distracted_by_multi_face": 0.03,
            "no_face": 0.03,
            "unknown": 0.03,
        }
        
        label = random.choices(
            list(label_weights.keys()),
            weights=list(label_weights.values()),
        )[0]
        
        # Generate realistic gaze/head pose based on label
        if label == "focused":
            gaze_yaw, gaze_pitch = random.gauss(0, 2), random.gauss(0, 2)
            head_yaw, head_pitch = random.gauss(0, 3), random.gauss(0, 3)
            eyes_open = random.uniform(0.8, 1.0)
            level = EngagementLevel.ENGAGED
        elif label == "looking_left":
            gaze_yaw, gaze_pitch = random.gauss(-15, 3), random.gauss(0, 2)
            head_yaw, head_pitch = random.gauss(-10, 3), random.gauss(0, 3)
            eyes_open = random.uniform(0.7, 1.0)
            level = EngagementLevel.PARTIAL
        elif label == "looking_right":
            gaze_yaw, gaze_pitch = random.gauss(15, 3), random.gauss(0, 2)
            head_yaw, head_pitch = random.gauss(10, 3), random.gauss(0, 3)
            eyes_open = random.uniform(0.7, 1.0)
            level = EngagementLevel.PARTIAL
        elif label == "sleepy":
            gaze_yaw, gaze_pitch = random.gauss(0, 5), random.gauss(-5, 3)
            head_yaw, head_pitch = random.gauss(0, 5), random.gauss(-5, 3)
            eyes_open = random.uniform(0.0, 0.3)
            level = EngagementLevel.NOT_ENGAGED
        else:
            gaze_yaw, gaze_pitch = random.gauss(0, 10), random.gauss(0, 10)
            head_yaw, head_pitch = random.gauss(0, 10), random.gauss(0, 10)
            eyes_open = random.uniform(0.5, 1.0)
            level = EngagementLevel.PARTIAL
        
        confidence = random.uniform(0.6, 0.95)
        
        event = EngagementEvent(
            session_id=session.id,
            attendance_id=attendance.id,
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(0, 60)),
            level=level,
            tab_switch=random.random() < 0.1,
            multiple_faces=label == "distracted_by_multi_face",
            labels=[{"name": label, "confidence": confidence}],
            gaze={"yaw": gaze_yaw, "pitch": gaze_pitch},
            head_pose={"x": head_yaw, "y": head_pitch, "z": 0},
            confidence=str(confidence),
            meta={
                "eyes_open_prob": eyes_open,
                "gaze_yaw": gaze_yaw,
                "gaze_pitch": gaze_pitch,
                "head_yaw": head_yaw,
                "head_pitch": head_pitch,
            },
        )
        db.add(event)
        events.append(event)
    
    db.commit()
    print(f"✓ Created {len(events)} engagement events")
    return events


def create_tab_switch_events(db, session, attendance_records, count=30):
    """Create tab switch events with some lock mode violations."""
    print(f"Creating {count} tab switch events...")
    
    events = []
    for _ in range(count):
        attendance = random.choice(attendance_records)
        
        # Some events are lock mode violations
        lock_mode_active = attendance.lock_mode
        lock_mode_violation = lock_mode_active and random.random() < 0.3
        
        event = TabSwitchEventLog(
            session_id=session.id,
            attendance_id=attendance.id,
            event_type="tab_switch",
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(0, 60)),
            tab_count=random.randint(1, 20),
            tab_visible=random.choice([True, False]),
            lock_mode_active=lock_mode_active,
            lock_mode_violation=lock_mode_violation,
            meta={"source": "test_data_generator"},
        )
        db.add(event)
        events.append(event)
    
    db.commit()
    print(f"✓ Created {len(events)} tab switch events")
    return events


def main():
    """Generate all test data."""
    print("\n" + "="*60)
    print("Focus Mate - Test Data Generator")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # Check if demo data already exists
        existing = db.query(User).filter(User.email.like("demo.%")).first()
        if existing:
            print("⚠ Demo data already exists!")
            response = input("Delete and regenerate? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
            
            # Clean up existing demo data
            print("\nCleaning up existing demo data...")
            db.query(TabSwitchEventLog).filter(
                TabSwitchEventLog.session_id.in_(
                    db.query(ClassSession.id).filter(
                        ClassSession.teacher_id.in_(
                            db.query(User.id).filter(User.email.like("demo.%"))
                        )
                    )
                )
            ).delete(synchronize_session=False)
            
            db.query(EngagementEvent).filter(
                EngagementEvent.session_id.in_(
                    db.query(ClassSession.id).filter(
                        ClassSession.teacher_id.in_(
                            db.query(User.id).filter(User.email.like("demo.%"))
                        )
                    )
                )
            ).delete(synchronize_session=False)
            
            db.query(Attendance).filter(
                Attendance.session_id.in_(
                    db.query(ClassSession.id).filter(
                        ClassSession.teacher_id.in_(
                            db.query(User.id).filter(User.email.like("demo.%"))
                        )
                    )
                )
            ).delete(synchronize_session=False)
            
            db.query(ClassSession).filter(
                ClassSession.teacher_id.in_(
                    db.query(User.id).filter(User.email.like("demo.%"))
                )
            ).delete(synchronize_session=False)
            
            db.query(User).filter(User.email.like("demo.%")).delete(synchronize_session=False)
            db.commit()
            print("✓ Cleaned up existing data\n")
        
        # Generate new data
        teacher, students = create_users(db)
        session = create_session(db, teacher)
        attendance_records = create_attendance(db, session, students)
        create_engagement_events(db, session, attendance_records, count=100)
        create_tab_switch_events(db, session, attendance_records, count=30)
        
        print("\n" + "="*60)
        print("✓ Test data generation complete!")
        print("="*60)
        print("\nDemo Credentials:")
        print("  Teacher: demo.teacher@focusmate.com / teacher123")
        print("  Students: demo.student1@focusmate.com / student123")
        print("            demo.student2@focusmate.com / student123")
        print("            ... (up to demo.student5)")
        print("\nSession Code: DEMO01")
        print("\nNext steps:")
        print("  1. Start backend: uvicorn app.main:app --reload")
        print("  2. Start frontend: npm run dev")
        print("  3. Login and explore the dashboard!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(130)
