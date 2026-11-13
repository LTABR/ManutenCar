from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import JSON, Date, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class User(Base):
    """Usuário autenticado pelo endpoint de login."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    # A coluna no MySQL continua se chamando "password" para manter
    # compatibilidade com o schema.sql e com os dados já existentes.
    password_hash: Mapped[str] = mapped_column("password", String(255), nullable=False)


class Car(Base):
    """Veículo pertencente a um ou mais usuários."""

    __tablename__ = "cars"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    brand: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    # Arrays JSON são mantidos por compatibilidade com o schema atual.
    # Em uma evolução futura podem ser substituídos por tabelas de junção.
    owners_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    parts_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    weekly_usage: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)


class Part(Base):
    """Peça acompanhada em um veículo, com a data da última revisão."""

    __tablename__ = "parts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    last_maintenance: Mapped[date] = mapped_column(Date, nullable=False)
    part_type_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)


class MaintenanceHistory(Base):
    """Histórico imutável (append-only) de manutenções realizadas.

    Cada criação ou atualização da última revisão de uma peça gera um
    registro nesta tabela. O histórico é mantido mesmo se a peça for
    removida do carro, pois representa o que já aconteceu no veículo.
    """

    __tablename__ = "maintenance_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    car_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    part_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    part_type_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    service_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    mileage: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )


def part_payload(part: Part) -> dict[str, Any]:
    """Serializa uma peça no formato esperado pelo frontend."""

    return {
        "id": part.id,
        "partId": part.part_type_id,
        "lastServiced": part.last_maintenance,
    }
