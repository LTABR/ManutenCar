from datetime import date
from typing import Any
from sqlalchemy import JSON, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base
from .maintenance import calculate_maintenance

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    password_hash: Mapped[str] = mapped_column("password", String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)

class Car(Base):
    __tablename__ = "cars"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    brand: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    owners_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    parts_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    weekly_usage: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

class Part(Base):
    __tablename__ = "parts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    last_maintenance: Mapped[date] = mapped_column(Date, nullable=False)
    part_type_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)

def part_payload(part: Part, weekly_usage_km: float = 0) -> dict[str, Any]:
    estimate = calculate_maintenance(
        part.part_type_id, part.last_maintenance, weekly_usage_km
    )
    return {
        "id": part.id,
        "partId": part.part_type_id,
        "lastServiced": part.last_maintenance.isoformat(),
        "last_maintenance": part.last_maintenance.isoformat(),
        "part_type_id": part.part_type_id,
        "expiresAt": estimate.expires_at.isoformat(),
        "calendarDue": estimate.calendar_due.isoformat(),
        "mileageDue": (
            estimate.mileage_due.isoformat() if estimate.mileage_due else None
        ),
        "wearPercent": estimate.wear_percent,
        "dueBy": estimate.due_by,
    }
