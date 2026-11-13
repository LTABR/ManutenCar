"""Cálculo dos prazos de manutenção.

A regra replica o comportamento do frontend (``src/pages/App.tsx``):

* prazo por tempo: data da última revisão + ``interval_months``;
* prazo por quilometragem: data da última revisão + dias estimados para
  percorrer ``interval_km`` com base no uso médio semanal do carro;
* o próximo vencimento é o menor entre os dois prazos.

Status:
* ``overdue``: prazo já passou;
* ``soon``: vence em até 45 dias;
* ``on-track``: vence em mais de 45 dias.
"""

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from math import ceil
from typing import Literal

from .models import Part
from .parts_catalog import get_part, part_name

ScheduleStatus = Literal["overdue", "soon", "on-track"]
DeadlineSource = Literal["time", "mileage"]


@dataclass(frozen=True)
class Deadline:
    """Resultado do cálculo de prazo de uma peça."""

    part_id: str
    part_type_id: str
    part_name: str
    last_service: date
    calendar_due: date
    mileage_due: date | None
    next_due: date
    days_until: int
    status: ScheduleStatus
    source: DeadlineSource


def add_months(value: date, months: int) -> date:
    """Soma meses a uma data, ajustando o dia ao último dia do mês.

    A implementação é equivalente à função ``addMonths`` do frontend,
    inclusive para datas como 31 de janeiro + 1 mês (resulta em 28/29 de
    fevereiro).
    """

    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(value.day, last_day))


def calendar_days_from_now(due: date, today: date | None = None) -> int:
    """Retorna a diferença em dias entre o vencimento e hoje."""

    reference = today or date.today()
    return (due - reference).days


def calculate_deadline(
    part: Part,
    weekly_usage: float,
    today: date | None = None,
) -> Deadline | None:
    """Calcula o prazo de uma peça.

    Retorna ``None`` quando o ``part_type_id`` não está no catálogo, pois
    sem os intervalos recomendados não é possível estimar um vencimento.
    """

    spec = get_part(part.part_type_id)
    if spec is None:
        return None

    reference = today or date.today()
    serviced_at = part.last_maintenance
    calendar_due = add_months(serviced_at, spec.interval_months)

    # O frontend converte o uso semanal para quilômetros por mês.
    km_per_month = max(float(weekly_usage or 0), 0) * 52 / 12
    mileage_due: date | None = None
    next_due = calendar_due
    source: DeadlineSource = "time"

    if km_per_month > 0:
        # 30.4375 é a média de dias por mês usada pelo frontend.
        estimated_days = ceil((spec.interval_km / km_per_month) * 30.4375)
        mileage_due = serviced_at + timedelta(days=estimated_days)
        if mileage_due < calendar_due:
            next_due = mileage_due
            source = "mileage"

    days_until = calendar_days_from_now(next_due, reference)
    if days_until < 0:
        status: ScheduleStatus = "overdue"
    elif days_until <= 45:
        status = "soon"
    else:
        status = "on-track"

    return Deadline(
        part_id=part.id,
        part_type_id=part.part_type_id,
        part_name=part_name(part.part_type_id),
        last_service=serviced_at,
        calendar_due=calendar_due,
        mileage_due=mileage_due,
        next_due=next_due,
        days_until=days_until,
        status=status,
        source=source,
    )


def car_deadlines(
    parts: list[Part],
    weekly_usage: float,
    today: date | None = None,
) -> list[Deadline]:
    """Calcula e ordena os prazos de todas as peças de um carro."""

    deadlines = [
        deadline
        for part in parts
        if (deadline := calculate_deadline(part, weekly_usage, today)) is not None
    ]
    return sorted(deadlines, key=lambda item: (item.next_due, item.part_type_id))
