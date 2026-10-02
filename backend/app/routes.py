from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .models import Car, Part, User, part_payload
from .schemas import (
    CarCreate,
    CarResponse,
    CarUpdate,
    EncryptedLogin,
    LoginResponse,
    PartCreate,
    PartResponse,
    PartUpdate,
    UserResponse,
)
from .security import create_access_token, decrypt_login_payload, get_current_user, verify_password

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
def login(payload: EncryptedLogin, db: Session = Depends(get_db)):
    try:
        credentials = decrypt_login_payload(payload.encryptedKey, payload.iv, payload.ciphertext)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    user = db.scalar(select(User).where(User.email == credentials["email"]))
    if not user or not verify_password(credentials["password"], user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login credentials")
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
    db.delete(car)
    db.commit()


@router.post("/cars/{car_id}/parts", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
def add_part(car_id: str, payload: PartCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    car = owned_car(db, user, car_id)
    part_type_id = payload.type_id()
    if not part_type_id:
        raise HTTPException(status_code=422, detail="part_type_id is required")
    part = Part(id=payload.id or str(uuid4()), part_type_id=part_type_id, last_maintenance=payload.maintenance_date())
    db.add(part)
    car.parts_ids = [*(car.parts_ids or []), part.id]
    db.commit()
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
    part.last_maintenance = payload.maintenance_date()
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
    if part:
        db.delete(part)
    db.commit()
