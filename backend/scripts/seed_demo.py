#!/usr/bin/env python3
"""Seed an idempotent Volkswagen Golf maintenance demo for existing accounts."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import select

from backend.app.db import Base, SessionLocal, engine
from backend.app.models import Car, MaintenanceRecord, Part, User


DEMO_EMAIL = "you@example.com"
DEMO_COMPONENTS = (
    ("spark-plugs", "Spark plugs", "Engine", 250),
    ("engine-oil", "Engine oil", "Engine", 500),
    ("coolant", "Coolant", "Fluids", 400),
    ("tires", "Tires", "Tires", 350),
    ("brake-pads", "Brakes", "Brakes", 1200),
)


def seed() -> tuple[int, int]:
    Base.metadata.create_all(bind=engine)
    today = date.today()
    with SessionLocal() as db:
        users = db.scalars(select(User).order_by(User.email)).all()
        if not any(user.email.casefold() == DEMO_EMAIL for user in users):
            raise RuntimeError(
                f"{DEMO_EMAIL} must already have an account; create it through the registration screen first."
            )

        cars_created = 0
        records_created = 0
        all_cars = db.scalars(select(Car)).all()
        for user in users:
            user_cars = [
                car
                for car in all_cars
                if user.id in (car.owners_ids or [])
                and car.model.casefold() == "volkswagen golf"
                and car.brand.casefold() in {"", "volkswagen"}
            ]
            car = min(user_cars, key=lambda candidate: len(candidate.parts_ids or []), default=None)
            if car is None:
                car = Car(
                    id=str(uuid4()),
                    brand="Volkswagen",
                    model="Volkswagen Golf",
                    owners_ids=[user.id],
                    parts_ids=[],
                    weekly_usage=300,
                )
                db.add(car)
                db.flush()
                cars_created += 1
            else:
                car.brand = "Volkswagen"
                car.weekly_usage = 300

            car_part_ids = list(car.parts_ids or [])
            parts_by_type = {
                part.part_type_id: part
                for part in db.scalars(select(Part).where(Part.id.in_(car_part_ids or [""]))).all()
            }
            for part_type_id, title, category, age_days in DEMO_COMPONENTS:
                part = parts_by_type.get(part_type_id)
                if part is None:
                    part = Part(
                        id=str(uuid4()),
                        part_type_id=part_type_id,
                        last_maintenance=today - timedelta(days=age_days),
                    )
                    db.add(part)
                    db.flush()
                    car_part_ids.append(part.id)
                    parts_by_type[part_type_id] = part
                if not db.scalar(
                    select(MaintenanceRecord.id)
                    .where(MaintenanceRecord.vehicle_id == car.id, MaintenanceRecord.part_id == part.id)
                    .limit(1)
                ):
                    current_service = part.last_maintenance
                    db.add_all(
                        [
                            MaintenanceRecord(
                                id=str(uuid4()),
                                vehicle_id=car.id,
                                part_id=part.id,
                                service_date=current_service - timedelta(days=365),
                                title=f"{title} service",
                                description=f"Previous {title.lower()} inspection.",
                                category=category,
                                status="completed",
                            ),
                            MaintenanceRecord(
                                id=str(uuid4()),
                                vehicle_id=car.id,
                                part_id=part.id,
                                service_date=current_service,
                                title=f"{title} service",
                                description=f"Recorded {title.lower()} maintenance.",
                                category=category,
                                status="completed",
                            ),
                        ]
                    )
                    records_created += 2
            car.parts_ids = car_part_ids

        db.commit()
        return cars_created, records_created


if __name__ == "__main__":
    created_cars, created_records = seed()
    print(f"Demo data complete: {created_cars} Volkswagen Golf vehicles created; {created_records} service records added.")
