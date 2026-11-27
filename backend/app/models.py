from datetime import date, datetime
from typing import Any
from sqlalchemy import CHAR, JSON, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    password_hash: Mapped[str] = mapped_column("password", String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)

class Car(Base):
    __tablename__ = "cars"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    brand: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    owners_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    parts_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    weekly_usage: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

class Part(Base):
    __tablename__ = "parts"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    last_maintenance: Mapped[date] = mapped_column(Date, nullable=False)
    part_type_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("cars.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False, index=True,
    )
    part_id: Mapped[str | None] = mapped_column(
        CHAR(36), ForeignKey("parts.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True, index=True,
    )
    service_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Open", index=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

def part_payload(part: Part) -> dict[str, Any]:
    return {
        "id": part.id,
        "partId": part.part_type_id,
        "lastServiced": part.last_maintenance.isoformat(),
        "last_maintenance": part.last_maintenance.isoformat(),
        "part_type_id": part.part_type_id,
    }
