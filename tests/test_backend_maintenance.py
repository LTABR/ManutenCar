from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base, get_db
from backend.app.main import app
from backend.app.models import Car, MaintenanceRecord, Part, User
from backend.app.security import get_current_user


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(
        test_engine,
        "connect",
        lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"),
    )
    testing_session = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(test_engine)
    with testing_session() as db:
        db.add_all(
            [
                User(id="user-owned", email="owner@example.com", password_hash="unused"),
                User(id="user-other", email="other@example.com", password_hash="unused"),
                Car(
                    id="car-owned",
                    brand="Volkswagen",
                    model="Volkswagen Golf",
                    owners_ids=["user-owned"],
                    parts_ids=[],
                    weekly_usage=300,
                ),
                Car(
                    id="car-other",
                    brand="Volkswagen",
                    model="Other Golf",
                    owners_ids=["user-other"],
                    parts_ids=[],
                    weekly_usage=300,
                ),
            ]
        )
        db.commit()

    def override_db():
        with testing_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: User(
        id="user-owned", email="owner@example.com", password_hash="unused"
    )
    test_client = TestClient(app)
    yield test_client, testing_session
    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


def test_owned_empty_vehicle_returns_empty_history_and_five_deadlines(client):
    client, _ = client
    history = client.get("/api/cars/car-owned/maintenance-history")
    deadlines = client.get("/api/cars/car-owned/maintenance-deadlines")

    assert history.status_code == 200
    assert history.json()["items"] == []
    assert history.json()["total"] == 0
    assert deadlines.status_code == 200
    assert [item["part_id"] for item in deadlines.json()] == [
        "spark-plugs",
        "engine-oil",
        "coolant",
        "tires",
        "brakes",
    ]
    assert all(item["status"] == "untracked" for item in deadlines.json())


def test_unowned_vehicle_is_hidden_and_chart_is_a_png(client):
    client, _ = client
    assert client.get("/api/cars/car-other/maintenance-history").status_code == 404
    assert client.get("/api/cars/car-other/maintenance-deadlines").status_code == 404

    chart = client.get("/api/cars/car-owned/maintenance-deadlines-chart")
    assert chart.status_code == 200
    assert chart.headers["content-type"] == "image/png"
    assert chart.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_python_deadline_rules_identify_overdue_and_current_components(client):
    client, testing_session = client
    today = date.today()
    with testing_session() as db:
        car = db.get(Car, "car-owned")
        oil = Part(
            id="oil-part",
            part_type_id="engine-oil",
            last_maintenance=today - timedelta(days=500),
        )
        plugs = Part(
            id="plugs-part",
            part_type_id="spark-plugs",
            last_maintenance=today - timedelta(days=30),
        )
        db.add_all([oil, plugs])
        car.parts_ids = [oil.id, plugs.id]
        db.commit()

    response = client.get("/api/cars/car-owned/maintenance-deadlines")
    statuses = {item["part_id"]: item["status"] for item in response.json()}
    assert statuses["engine-oil"] == "overdue"
    assert statuses["spark-plugs"] == "on-track"


def test_add_part_persists_car_foreign_key_and_maintenance_record(client):
    client, testing_session = client

    response = client.post(
        "/api/cars/car-owned/parts",
        json={"partId": "engine-oil", "lastServiced": date.today().isoformat()},
    )

    assert response.status_code == 201
    part_id = response.json()["id"]
    with testing_session() as db:
        part = db.get(Part, part_id)
        record = db.scalar(
            select(MaintenanceRecord).where(MaintenanceRecord.part_id == part_id)
        )

    assert part.car_id == "car-owned"
    assert record.vehicle_id == "car-owned"
    assert record.part_id == part_id
