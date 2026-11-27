from __future__ import annotations

from datetime import date, timedelta
from math import ceil

from .models import Car, Part
from .schemas import MaintenanceDeadlineResponse

MANDATORY_COMPONENTS: tuple[tuple[str, tuple[str, ...], int, int], ...] = (
    ("spark-plugs", ("spark-plugs",), 40_000, 36),
    ("engine-oil", ("engine-oil",), 10_000, 12),
    ("coolant", ("coolant",), 40_000, 36),
    ("tires", ("tires",), 40_000, 36),
    ("brakes", ("brake-pads", "brake-fluid"), 40_000, 36),
)


def add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    next_month = date(year + (month == 12), month % 12 + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    return date(year, month, min(start.day, last_day))


def calculate_mandatory_deadlines(
    car: Car,
    parts: list[Part],
    *,
    today: date | None = None,
) -> list[MaintenanceDeadlineResponse]:
    reference_date = today or date.today()
    attached = {part.id: part for part in parts if part.id in (car.parts_ids or [])}
    by_type = {part.part_type_id: part for part in attached.values()}
    results: list[MaintenanceDeadlineResponse] = []

    for component_id, accepted_types, interval_km, interval_months in MANDATORY_COMPONENTS:
        part = next((by_type[part_type] for part_type in accepted_types if part_type in by_type), None)
        if part is None:
            results.append(
                MaintenanceDeadlineResponse(
                    part_id=component_id,
                    last_serviced=None,
                    due_date=None,
                    days_until=None,
                    status="untracked",
                )
            )
            continue

        calendar_due = add_months(part.last_maintenance, interval_months)
        weekly_usage = float(car.weekly_usage or 0)
        mileage_due = (
            part.last_maintenance + timedelta(days=ceil(interval_km / weekly_usage * 7))
            if weekly_usage > 0
            else calendar_due
        )
        due_date = min(calendar_due, mileage_due)
        days_until = (due_date - reference_date).days
        deadline_status = "overdue" if days_until < 0 else "soon" if days_until <= 45 else "on-track"
        results.append(
            MaintenanceDeadlineResponse(
                part_id=component_id,
                last_serviced=part.last_maintenance,
                due_date=due_date,
                days_until=days_until,
                status=deadline_status,
            )
        )
    return results
