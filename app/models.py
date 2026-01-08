from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Boolean, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base

class Person(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    embeddings = relationship("Embedding", back_populates="person", cascade="all, delete-orphan")

class Embedding(Base):
    __tablename__ = "embeddings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), index=True)
    vec_csv: Mapped[str] = mapped_column(String, nullable=False)
    person = relationship("Person", back_populates="embeddings")

class AttendancePolicy(Base):
    __tablename__ = "attendance_policy"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # single row: id=1
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Jakarta")
    in_start_time: Mapped[str] = mapped_column(String(5), default="05:00")
    late_after_time: Mapped[str] = mapped_column(String(5), default="08:00")
    out_start_time: Mapped[str] = mapped_column(String(5), default="15:00")
    retention_days: Mapped[int] = mapped_column(Integer, default=60)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AttendanceEvent(Base):
    __tablename__ = "attendance_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # day in local policy timezone at record time
    day: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD

    # store UTC naive for simplicity
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    device_id: Mapped[str] = mapped_column(String(80), index=True)

    predicted_name: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    final_name: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)

    event_type: Mapped[str | None] = mapped_column(String(3), nullable=True)  # IN/OUT
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[str] = mapped_column(String(40))  # ok/unknown/reject/error/duplicate/cooldown/reject_out_too_early
    distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    snapshot_path: Mapped[str | None] = mapped_column(String, nullable=True)

    # audit trail (koreksi admin)
    edited_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    edited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    edit_note: Mapped[str | None] = mapped_column(Text, nullable=True)

class DailyAttendance(Base):
    __tablename__ = "daily_attendance"
    __table_args__ = (UniqueConstraint("day", "person_name", name="uq_day_person"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD
    person_name: Mapped[str] = mapped_column(String(120), index=True)

    in_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    in_is_late: Mapped[bool] = mapped_column(Boolean, default=False)

    out_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AdminUser(Base):
    __tablename__ = "admin_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AdminSession(Base):
    __tablename__ = "admin_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)