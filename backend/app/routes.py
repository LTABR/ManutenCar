from uuid import uuid4

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import get_db
from .models import Car, MaintenanceRecord, Part, SupportTicket, User, part_payload
from .maintenance_charts import MaintenanceDeadline, render_deadline_chart
from .maintenance_deadlines import calculate_mandatory_deadlines
from .maintenance_history import query_maintenance_history
from .schemas import (
    CarCreate,
    CarResponse,
    CarUpdate,
    EncryptedAuthPayload,
    LoginResponse,
    PartCreate,
    PartResponse,
    PartUpdate,
    UserResponse,
    MaintenanceDeadlineResponse,
    MaintenanceDeadlinesRequest,
    MaintenanceHistoryResponse,
    SupportTicketCreate,
    SupportTicketResponse,
)
from .security import (
    create_access_token,
    decrypt_auth_payload,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter()


def user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, name=user.email.split("@", 1)[0], email=user.email)


def owned_car(db: Session, user: User, car_id: str) -> Car:
    car = db.get(Car, car_id)
    if not car or user.id not in (car.owners_ids or []):
        raise HTTPException(status_code=404, detail="Car not found")
    return car


def response_car(db: Session, car: Car) -> CarResponse:
    parts = db.scalars(select(Part).where(Part.id.in_(car.parts_ids or []))).all() if car.parts_ids else []
    weekly_usage = float(car.weekly_usage or 0)
    return CarResponse(
        id=car.id,
        brand=car.brand,
        model=car.model,
        owners_ids=car.owners_ids or [],
        parts_ids=car.parts_ids or [],
        weekly_usage=weekly_usage,
        distance=str(round(weekly_usage, 2)),
        frequency="week",
        parts=[part_payload(part) for part in parts],
    )


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: EncryptedAuthPayload, db: Session = Depends(get_db)):
    try:
        credentials = decrypt_auth_payload(payload.encryptedKey, payload.iv, payload.ciphertext)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    user = db.scalar(select(User).where(User.email == credentials["email"]))
    if not user or not verify_password(credentials["password"], user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return LoginResponse(accessToken=create_access_token(user.id), user=user_response(user))


@router.post("/auth/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(payload: EncryptedAuthPayload, db: Session = Depends(get_db)):
    try:
        credentials = decrypt_auth_payload(payload.encryptedKey, payload.iv, payload.ciphertext)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid registration payload")
    email = credentials["email"]
    if (
        len(email) > 320
        or email.count("@") != 1
        or any(character.isspace() for character in email)
        or not all(email.split("@"))
    ):
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    if len(credentials["password"]) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(
        id=str(uuid4()),
        email=email,
        password_hash=hash_password(credentials["password"]),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    db.refresh(user)
    return LoginResponse(accessToken=create_access_token(user.id), user=user_response(user))


@router.get("/cars", response_model=list[CarResponse])
def list_cars(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cars = db.scalars(select(Car)).all()
    return [response_car(db, car) for car in cars if user.id in (car.owners_ids or [])]


@router.post("/cars", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def create_car(payload: CarCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = Car(
        id=str(uuid4()),
        brand=payload.brand,
        model=payload.model,
        owners_ids=[user.id],
        parts_ids=[],
        weekly_usage=payload.weekly_km(),
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    return response_car(db, car)


@router.patch("/cars/{car_id}", response_model=CarResponse)
def update_car(car_id: str, payload: CarUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = owned_car(db, user, car_id)
    values = payload.model_dump(exclude_unset=True)
    if "distance" in values:
        payload_distance = values.pop("distance")
        try:
            distance = max(float(payload_distance or 0), 0)
        except (TypeError, ValueError):
            distance = 0
        frequency = values.get("frequency", "week")
        values["weekly_usage"] = {"week": distance, "month": distance * 12 / 52, "year": distance / 52}.get(frequency, distance)
    values.pop("frequency", None)
    for key, value in values.items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return response_car(db, car)


@router.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = owned_car(db, user, car_id)
    removed_part_ids = set(car.parts_ids or [])
    other_cars = db.scalars(select(Car).where(Car.id != car_id)).all()
    referenced_part_ids = {
        part_id
        for other_car in other_cars
        for part_id in (other_car.parts_ids or [])
    }
    db.delete(car)
    for part_id in removed_part_ids - referenced_part_ids:
        part = db.get(Part, part_id)
        if part:
            db.delete(part)
    db.commit()


def _car_deadlines(db: Session, car: Car):
    parts = db.scalars(select(Part).where(Part.id.in_(car.parts_ids or []))).all()
    return calculate_mandatory_deadlines(car, parts)


@router.get(
    "/cars/{vehicle_id}/maintenance-deadlines",
    response_model=list[MaintenanceDeadlineResponse],
)
def get_maintenance_deadlines(
    vehicle_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    car = owned_car(db, user, vehicle_id)
    return _car_deadlines(db, car)


@router.get("/cars/{vehicle_id}/maintenance-deadlines-chart")
def get_maintenance_deadlines_chart(
    vehicle_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    car = owned_car(db, user, vehicle_id)
    tracked = [
        deadline
        for deadline in _car_deadlines(db, car)
        if deadline.days_until is not None
    ]
    chart = render_deadline_chart(
        MaintenanceDeadline(
            label=deadline.part_id.replace("-", " ").title(),
            days_until=deadline.days_until,
        )
        for deadline in tracked
    )
    return StreamingResponse(
        chart,
        media_type="image/png",
        headers={
            "Content-Disposition": 'inline; filename="maintenance-deadlines.png"',
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/cars/{vehicle_id}/maintenance-history",
    response_model=MaintenanceHistoryResponse,
)
def get_maintenance_history(
    vehicle_id: str,
    keyword: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    category: str | None = None,
    record_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_car(db, user, vehicle_id)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")
    records, total = query_maintenance_history(
        db,
        vehicle_id,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
        category=category,
        status=record_status,
        limit=limit,
        offset=offset,
    )
    return MaintenanceHistoryResponse(
        items=[
            {
                "id": record.id,
                "vehicle_id": record.vehicle_id,
                "part_id": record.part_id,
                "part_name": part_name,
                "service_date": record.service_date,
                "title": record.title,
                "description": record.description,
                "category": record.category,
                "status": record.status,
            }
            for record, part_name in records
        ],
        total=total,
        page=offset // limit + 1,
        page_size=limit,
    )


@router.post("/cars/{vehicle_id}/maintenance-deadlines-chart")
def post_maintenance_deadlines_chart(
    vehicle_id: str,
    payload: MaintenanceDeadlinesRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_car(db, user, vehicle_id)
    chart = render_deadline_chart(
        MaintenanceDeadline(label=item.label, days_until=item.days_until)
        for item in payload.deadlines
    )
    return StreamingResponse(
        chart,
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename="maintenance-deadlines.png"'},
    )


@router.post("/cars/{car_id}/parts", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
def add_part(car_id: str, payload: PartCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = owned_car(db, user, car_id)
    part_type_id = payload.type_id()
    if not part_type_id or len(part_type_id) > 80:
        raise HTTPException(status_code=422, detail="part_type_id is required")
    if any(
        existing_part.part_type_id == part_type_id
        for existing_part in db.scalars(
            select(Part).where(Part.id.in_(car.parts_ids or []))
        )
    ):
        raise HTTPException(status_code=409, detail="This part is already tracked for this car")

    part = Part(
        id=str(uuid4()),
        part_type_id=part_type_id,
        last_maintenance=payload.maintenance_date(),
    )
    db.add(part)
    car.parts_ids = [*(car.parts_ids or []), part.id]
    db.add(
        MaintenanceRecord(
            id=str(uuid4()),
            vehicle_id=car.id,
            part_id=part.id,
            service_date=part.last_maintenance,
            title=part_type_id,
            category=part_type_id,
            status="completed",
        )
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(part)
    return part_payload(part)


@router.patch("/cars/{car_id}/parts/{part_id}", response_model=PartResponse)
def update_part(car_id: str, part_id: str, payload: PartUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = owned_car(db, user, car_id)
    if part_id not in (car.parts_ids or []):
        raise HTTPException(status_code=404, detail="Part not found")
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    service_date = payload.maintenance_date()
    if service_date != part.last_maintenance:
        db.add(
            MaintenanceRecord(
                id=str(uuid4()),
                vehicle_id=car.id,
                part_id=part.id,
                service_date=service_date,
                title=part.part_type_id,
                category=part.part_type_id,
                status="completed",
            )
        )
    part.last_maintenance = service_date
    db.commit()
    db.refresh(part)
    return part_payload(part)


@router.delete("/cars/{car_id}/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_part(car_id: str, part_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = owned_car(db, user, car_id)
    if part_id not in (car.parts_ids or []):
        raise HTTPException(status_code=404, detail="Part not found")
    car.parts_ids = [value for value in car.parts_ids if value != part_id]
    part = db.get(Part, part_id)
    other_cars = db.scalars(select(Car).where(Car.id != car_id)).all()
    still_referenced = any(
        part_id in (other_car.parts_ids or []) for other_car in other_cars
    )
    if part and not still_referenced:
        db.delete(part)
    db.commit()


@router.post("/support/tickets", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
def create_support_ticket(payload: SupportTicketCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = SupportTicket(
        id=str(uuid4()),
        user_id=user.id,
        category=payload.category,
        subject=payload.subject.strip(),
        description=payload.description.strip(),
        status="Open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/support/tickets", response_model=list[SupportTicketResponse])
def list_support_tickets(
    category: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(SupportTicket).where(SupportTicket.user_id == user.id)
    if category:
        query = query.where(SupportTicket.category == category)
    if status_filter:
        if status_filter not in {"Open", "In Progress", "Resolved"}:
            raise HTTPException(status_code=422, detail="Invalid ticket status")
        query = query.where(SupportTicket.status == status_filter)
    return db.scalars(query.order_by(SupportTicket.created_at.desc())).all()
