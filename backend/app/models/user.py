from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as PgEnum, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserRole(str, Enum):
    TEACHER = "teacher"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(PgEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    classes = relationship("ClassSession", back_populates="teacher")
    attendance = relationship("Attendance", back_populates="student")

