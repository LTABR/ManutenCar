from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from math import ceil, isfinite
from typing import Literal

from scipy.optimize import brentq


PART_INTERVALS: dict[str, tuple[int, int]] = {
    "engine-oil": (10_000, 12),
    "air-filter": (20_000, 24),
    "cabin-filter": (15_000, 12),
    "brake-fluid": (40_000, 24),
    "brake-pads": (40_000, 36),
    "spark-plugs": (40_000, 36),
    "coolant": (40_000, 36),
    "timing-belt": (100_000, 60),
    "battery": (60_000, 48),
}


@dataclass(frozen=True)
class MaintenanceEstimate:
    calendar_due: date
    mileage_due: date | None
    expires_at: date
    wear_percent: float
    due_by: Literal["time", "mileage"]


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


def calculate_maintenance(
    part_type_id: str,
    last_maintenance: date,
    weekly_usage_km: float,
    as_of: date | None = None,
) -> MaintenanceEstimate:
    """Estimate component wear and expiry from calendar age and expected mileage."""
    try:
        interval_km, interval_months = PART_INTERVALS[part_type_id]
    except KeyError as error:
        raise ValueError(f"Unknown part type: {part_type_id}") from error

    today = as_of or date.today()
    weekly_usage = float(weekly_usage_km)
    if not isfinite(weekly_usage):
        raise ValueError("Weekly usage must be a finite number")
    weekly_usage = max(weekly_usage, 0.0)
    calendar_due = _add_months(last_maintenance, interval_months)
    calendar_interval_days = (calendar_due - last_maintenance).days
    mileage_interval_days = (
        interval_km * 7 / weekly_usage if weekly_usage > 0 else None
    )
    mileage_days = (
        ceil(mileage_interval_days) if mileage_interval_days is not None else None
    )
    mileage_due = None
    if mileage_days is not None:
        try:
            mileage_due = last_maintenance + timedelta(days=mileage_days)
        except OverflowError:
            pass

    def wear_after(days: float) -> float:
        calendar_wear = days / calendar_interval_days
        mileage_wear = days * weekly_usage / (7 * interval_km)
        return max(calendar_wear, mileage_wear)

    expiry_bound = min(
        calendar_interval_days,
        (
            mileage_interval_days
            if mileage_interval_days is not None
            else calendar_interval_days
        ),
    )
    days_until_expiry = ceil(
        brentq(lambda days: wear_after(days) - 1, 0, expiry_bound) - 1e-9
    )
    expires_at = last_maintenance + timedelta(days=days_until_expiry)
    due_by: Literal["time", "mileage"] = (
        "mileage"
        if mileage_interval_days is not None
        and mileage_interval_days < calendar_interval_days
        else "time"
    )

    elapsed_days = max((today - last_maintenance).days, 0)
    wear_percent = min(wear_after(elapsed_days) * 100, 100.0)
    return MaintenanceEstimate(
        calendar_due=calendar_due,
        mileage_due=mileage_due,
        expires_at=expires_at,
        wear_percent=round(wear_percent, 1),
        due_by=due_by,
    )
