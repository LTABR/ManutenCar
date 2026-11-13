"""Testes do histórico de manutenções e da geração do gráfico de prazos."""

from conftest import auth_headers, create_user


def _create_car(client, headers, brand="Toyota", model="Corolla", weekly_usage=250):
    response = client.post(
        "/api/cars",
        json={"brand": brand, "model": model, "weekly_usage": weekly_usage},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _add_part(client, headers, car_id, part_type_id, service_date):
    response = client.post(
        f"/api/cars/{car_id}/parts",
        json={"part_type_id": part_type_id, "lastServiced": service_date},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_part_creation_generates_history(client_and_session):
    client, sessions = client_and_session
    _, token = create_user(sessions, "owner@example.com")
    headers = auth_headers(token)
    car_id = _create_car(client, headers)
    part_id = _add_part(client, headers, car_id, "engine-oil", "2024-01-10")

    response = client.get(f"/api/cars/{car_id}/maintenance-history", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["limit"] == 20
    assert payload["offset"] == 0
    assert payload["items"][0]["id"]
    assert payload["items"][0]["car_id"] == car_id
    assert payload["items"][0]["part_id"] == part_id
    assert payload["items"][0]["part_type_id"] == "engine-oil"
    assert payload["items"][0]["part_name"] == "Engine oil & filter"
    assert payload["items"][0]["service_date"] == "2024-01-10"


def test_history_filters_search_pagination_and_order(client_and_session):
    client, sessions = client_and_session
    _, token = create_user(sessions, "filters@example.com")
    headers = auth_headers(token)
    car_id = _create_car(client, headers)
    _add_part(client, headers, car_id, "engine-oil", "2024-01-10")
    brake_part_id = _add_part(client, headers, car_id, "brake-pads", "2024-03-15")

    by_type = client.get(
        f"/api/cars/{car_id}/maintenance-history",
        params={"part_type_id": "brake-pads"},
        headers=headers,
    )
    assert by_type.status_code == 200
    assert by_type.json()["total"] == 1
    assert by_type.json()["items"][0]["part_id"] == brake_part_id

    by_name = client.get(
        f"/api/cars/{car_id}/maintenance-history",
        params={"search": "brake"},
        headers=headers,
    )
    assert by_name.status_code == 200
    assert by_name.json()["total"] == 1
    assert by_name.json()["items"][0]["part_type_id"] == "brake-pads"

    by_period = client.get(
        f"/api/cars/{car_id}/maintenance-history",
        params={"date_from": "2024-03-01", "date_to": "2024-03-31"},
        headers=headers,
    )
    assert by_period.status_code == 200
    assert by_period.json()["total"] == 1

    paginated = client.get(
        f"/api/cars/{car_id}/maintenance-history",
        params={"limit": 1, "offset": 1, "order": "asc"},
        headers=headers,
    )
    assert paginated.status_code == 200
    assert paginated.json()["total"] == 2
    assert len(paginated.json()["items"]) == 1
    assert paginated.json()["items"][0]["service_date"] == "2024-03-15"


def test_part_update_appends_new_history_entry(client_and_session):
    client, sessions = client_and_session
    _, token = create_user(sessions, "update@example.com")
    headers = auth_headers(token)
    car_id = _create_car(client, headers)
    part_id = _add_part(client, headers, car_id, "engine-oil", "2024-01-10")

    response = client.patch(
        f"/api/cars/{car_id}/parts/{part_id}",
        json={"lastServiced": "2024-06-20"},
        headers=headers,
    )
    assert response.status_code == 200, response.text

    history = client.get(
        f"/api/cars/{car_id}/maintenance-history",
        params={"order": "desc"},
        headers=headers,
    ).json()
    assert history["total"] == 2
    assert history["items"][0]["service_date"] == "2024-06-20"
    assert history["items"][1]["service_date"] == "2024-01-10"

    # Reenviar a mesma data não deve duplicar o evento no histórico.
    client.patch(
        f"/api/cars/{car_id}/parts/{part_id}",
        json={"lastServiced": "2024-06-20"},
        headers=headers,
    )
    unchanged = client.get(
        f"/api/cars/{car_id}/maintenance-history",
        headers=headers,
    ).json()
    assert unchanged["total"] == 2


def test_history_is_scoped_to_authenticated_user(client_and_session):
    client, sessions = client_and_session
    _, owner_token = create_user(sessions, "owner2@example.com")
    _, other_token = create_user(sessions, "other@example.com")
    owner_headers = auth_headers(owner_token)
    other_headers = auth_headers(other_token)
    car_id = _create_car(client, owner_headers)
    _add_part(client, owner_headers, car_id, "engine-oil", "2024-01-10")

    forbidden = client.get(
        f"/api/cars/{car_id}/maintenance-history",
        headers=other_headers,
    )
    assert forbidden.status_code == 404

    other_car_id = _create_car(client, other_headers, brand="Honda", model="Civic")
    _add_part(client, other_headers, other_car_id, "brake-pads", "2024-02-01")

    owner_global = client.get("/api/maintenance-history", headers=owner_headers)
    assert owner_global.status_code == 200
    assert owner_global.json()["total"] == 1
    assert owner_global.json()["items"][0]["car_id"] == car_id

    other_global = client.get("/api/maintenance-history", headers=other_headers)
    assert other_global.status_code == 200
    assert other_global.json()["total"] == 1
    assert other_global.json()["items"][0]["car_id"] == other_car_id


def test_history_requires_authentication(client_and_session):
    client, _ = client_and_session
    response = client.get("/api/maintenance-history")
    assert response.status_code == 401


def test_deleting_car_removes_its_history(client_and_session):
    client, sessions = client_and_session
    _, token = create_user(sessions, "delete@example.com")
    headers = auth_headers(token)
    car_id = _create_car(client, headers)
    _add_part(client, headers, car_id, "engine-oil", "2024-01-10")

    response = client.delete(f"/api/cars/{car_id}", headers=headers)
    assert response.status_code == 204

    db = sessions()
    try:
        from app.models import MaintenanceHistory
        from sqlalchemy import func, select

        total = db.scalar(select(func.count()).select_from(MaintenanceHistory))
        assert total == 0
    finally:
        db.close()


def test_deadline_chart_returns_png(client_and_session):
    client, sessions = client_and_session
    _, token = create_user(sessions, "chart@example.com")
    headers = auth_headers(token)
    car_id = _create_car(client, headers)
    _add_part(client, headers, car_id, "engine-oil", "2024-01-10")
    _add_part(client, headers, car_id, "brake-pads", "2024-03-15")

    response = client.get(f"/api/cars/{car_id}/deadline-chart", headers=headers)

    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(response.content) > 1000


def test_deadline_chart_requires_owned_car_with_known_parts(client_and_session):
    client, sessions = client_and_session
    _, token = create_user(sessions, "emptychart@example.com")
    headers = auth_headers(token)
    car_id = _create_car(client, headers)

    no_parts = client.get(f"/api/cars/{car_id}/deadline-chart", headers=headers)
    assert no_parts.status_code == 404

    _, other_token = create_user(sessions, "otherchart@example.com")
    forbidden = client.get(
        f"/api/cars/{car_id}/deadline-chart",
        headers=auth_headers(other_token),
    )
    assert forbidden.status_code == 404
