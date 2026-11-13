"""Testes unitários do cálculo de prazos usado pelo gráfico."""

from datetime import date

from app.deadlines import add_months, calculate_deadline, car_deadlines
from app.models import Part


def test_add_months_clamps_day_to_end_of_month():
    assert add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)
    assert add_months(date(2023, 1, 31), 1) == date(2023, 2, 28)
    assert add_months(date(2024, 11, 30), 3) == date(2025, 2, 28)


def test_time_based_deadline_without_mileage():
    part = Part(
        id="part-1",
        part_type_id="engine-oil",
        last_maintenance=date(2024, 1, 10),
    )

    deadline = calculate_deadline(part, weekly_usage=0, today=date(2024, 1, 1))

    assert deadline is not None
    assert deadline.calendar_due == date(2025, 1, 10)
    assert deadline.mileage_due is None
    assert deadline.next_due == deadline.calendar_due
    assert deadline.source == "time"
    assert deadline.status == "on-track"


def test_mileage_based_deadline_can_be_earlier_than_time():
    part = Part(
        id="part-1",
        part_type_id="engine-oil",
        last_maintenance=date(2024, 1, 10),
    )

    deadline = calculate_deadline(part, weekly_usage=250, today=date(2024, 1, 10))

    assert deadline is not None
    assert deadline.mileage_due is not None
    assert deadline.mileage_due < deadline.calendar_due
    assert deadline.next_due == deadline.mileage_due
    assert deadline.source == "mileage"


def test_overdue_and_soon_status():
    overdue = calculate_deadline(
        Part(
            id="part-1",
            part_type_id="engine-oil",
            last_maintenance=date(2022, 1, 1),
        ),
        weekly_usage=0,
        today=date(2024, 1, 1),
    )
    soon = calculate_deadline(
        Part(
            id="part-2",
            part_type_id="engine-oil",
            last_maintenance=date(2024, 1, 1),
        ),
        weekly_usage=0,
        today=date(2024, 12, 20),
    )

    assert overdue is not None and overdue.status == "overdue"
    assert soon is not None and soon.status == "soon"


def test_unknown_part_type_has_no_deadline():
    part = Part(
        id="part-1",
        part_type_id="unknown-part",
        last_maintenance=date(2024, 1, 1),
    )
    assert calculate_deadline(part, weekly_usage=0, today=date(2024, 1, 1)) is None


def test_car_deadlines_are_sorted_by_next_due_date():
    parts = [
        Part(id="p1", part_type_id="battery", last_maintenance=date(2024, 1, 1)),
        Part(id="p2", part_type_id="engine-oil", last_maintenance=date(2024, 1, 1)),
    ]

    deadlines = car_deadlines(parts, weekly_usage=0, today=date(2024, 1, 1))

    assert [item.part_type_id for item in deadlines] == ["engine-oil", "battery"]
