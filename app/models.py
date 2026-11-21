from datetime import date

from sqlalchemy import Date, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    brand: Mapped[str] = mapped_column(String(120), default="")
    model: Mapped[str] = mapped_column(String(120), default="")
    owners_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    parts_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    weekly_usage: Mapped[float] = mapped_column(Float, default=0)


class Part(Base):
    __tablename__ = "parts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    part_type_id: Mapped[str] = mapped_column(String(120), index=True)
    last_maintenance: Mapped[date] = mapped_column(Date)


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String(36), index=True)
    part_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    service_date: Mapped[date] = mapped_column(Date, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)


def part_payload(part: Part) -> dict[str, str | date]:
    return {
        "id": part.id,
        "partId": part.part_type_id,
        "lastServiced": part.last_maintenance,
    }
