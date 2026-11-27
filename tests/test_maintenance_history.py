from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import Car, MaintenanceRecord, Part, User
from app.security import get_current_user


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with TestingSession() as db:
        user = User(id="user-1", email="driver@example.com", password_hash="unused")
        car = Car(
            id="car-1", brand="Example", model="Roadster", owners_ids=[user.id],
            parts_ids=["part-1"], weekly_usage=100,
        )
        part = Part(id="part-1", part_type_id="engine-oil", last_maintenance=date(2025, 1, 10))
        records = [
            MaintenanceRecord(
                id="record-old", vehicle_id=car.id, part_id=part.id,
                service_date=date(2025, 1, 10), title="Oil change",
                description="Replaced engine oil", category="engine", status="completed",
            ),
            MaintenanceRecord(
                id="record-new", vehicle_id=car.id, part_id=part.id,
                service_date=date(2025, 6, 20), title="Filter service",
                description="Cabin filter replacement", category="comfort", status="completed",
            ),
            MaintenanceRecord(
                id="record-other-car", vehicle_id="car-2", part_id=None,
                service_date=date(2025, 8, 1), title="Other vehicle service",
            ),
        ]
        db.add_all([user, car, part, *records])
        db.commit()

    def override_db():
        with TestingSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: User(
        id="user-1", email="driver@example.com", password_hash="unused"
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_history_returns_records_newest_first(client: TestClient):
    response = client.get("/api/cars/car-1/maintenance-history")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert [item["id"] for item in payload["items"]] == ["record-new", "record-old"]
    assert payload["items"][0]["part_name"] == "engine-oil"


def test_history_searches_and_filters(client: TestClient):
    response = client.get(
        "/api/cars/car-1/maintenance-history",
        params={
            "keyword": "CABIN",
            "start_date": "2025-06-01",
            "end_date": "2025-06-30",
            "category": "COMFORT",
            "status": "completed",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == "record-new"


def test_history_paginates_and_returns_empty_results(client: TestClient):
    page = client.get("/api/cars/car-1/maintenance-history?limit=1&offset=1")
    empty = client.get("/api/cars/car-1/maintenance-history?keyword=not-found")

    assert page.status_code == 200
    assert page.json()["page"] == 2
    assert page.json()["total"] == 2
    assert len(page.json()["items"]) == 1
    assert empty.status_code == 200
    assert empty.json()["items"] == []
    assert empty.json()["total"] == 0


def test_history_returns_404_for_unknown_or_unowned_vehicle(client: TestClient):
    response = client.get("/api/cars/missing-car/maintenance-history")

    assert response.status_code == 404


def test_deadline_chart_returns_png_for_owned_vehicle(client: TestClient):
    response = client.post(
        "/api/cars/car-1/maintenance-deadlines-chart",
        json={"deadlines": [{"label": "Engine oil", "days_until": -4}]},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
