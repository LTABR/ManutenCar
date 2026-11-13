from typing import Any, Literal
from uuid import uuid4

import jwt
from email.mime.text import MIMEText
import smtplib

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .deadlines import car_deadlines
from .models import Car, MaintenanceHistory, Part, User, part_payload
from .parts_catalog import matching_part_ids, part_name
from .schemas import (
    CarCreate,
    CarResponse,
    CarUpdate,
    EmailRequest,
    EncryptedLogin,
    LoginResponse,
    MaintenanceHistoryItem,
    MaintenanceHistoryPage,
    PartCreate,
    PartResponse,
    PartUpdate,
    TokenConfirm,
    UserCreate,
    UserResponse,
)
from .security import (
    create_access_token,
    decrypt_login_payload,
    get_current_user,
    hash_password,
    verify_password,
)
from .visualization import render_deadline_chart
from datetime import date, datetime, timedelta

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


def record_maintenance(
    db: Session,
    car: Car,
    part: Part,
    service_date: date,
    mileage: float | None = None,
    notes: str | None = None,
) -> MaintenanceHistory:
    """Adiciona um evento ao histórico imutável de manutenções.

    O registro é criado automaticamente ao adicionar uma peça ou ao
    atualizar a data da última revisão. O histórico nunca é sobrescrito.
    """

    record = MaintenanceHistory(
        id=str(uuid4()),
        car_id=car.id,
        part_id=part.id,
        part_type_id=part.part_type_id,
        service_date=service_date,
        mileage=mileage,
        notes=notes,
    )
    db.add(record)
    return record


def history_item(record: MaintenanceHistory) -> MaintenanceHistoryItem:
    """Converte o model do histórico no schema de resposta da API."""

    return MaintenanceHistoryItem(
        id=record.id,
        car_id=record.car_id,
        part_id=record.part_id,
        part_type_id=record.part_type_id,
        part_name=part_name(record.part_type_id, record.part_type_id),
        service_date=record.service_date,
        mileage=float(record.mileage) if record.mileage is not None else None,
        notes=record.notes,
        created_at=record.created_at,
    )


def owned_car_ids(db: Session, user: User) -> list[str]:
    """Lista os ids de todos os carros pertencentes ao usuário autenticado."""

    cars = db.scalars(select(Car)).all()
    return [car.id for car in cars if user.id in (car.owners_ids or [])]


def maintenance_history_page(
    db: Session,
    user: User,
    car_id: str | None = None,
    part_id: str | None = None,
    part_type_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    order: Literal["asc", "desc"] = "desc",
    limit: int = 20,
    offset: int = 0,
) -> MaintenanceHistoryPage:
    """Monta a busca paginada e autenticada do histórico de manutenções.

    Quando ``car_id`` é informado, valida a propriedade do carro antes de
    consultar. Caso contrário, restringe a busca aos carros do usuário.
    """

    conditions: list[Any] = []
    if car_id is not None:
        # A validação de propriedade evita que um usuário consulte o
        # histórico de um carro que não é seu.
        conditions.append(MaintenanceHistory.car_id == owned_car(db, user, car_id).id)
    else:
        conditions.append(MaintenanceHistory.car_id.in_(owned_car_ids(db, user)))

    if part_id:
        conditions.append(MaintenanceHistory.part_id == part_id)
    if part_type_id:
        conditions.append(MaintenanceHistory.part_type_id == part_type_id)
    if date_from:
        conditions.append(MaintenanceHistory.service_date >= date_from)
    if date_to:
        conditions.append(MaintenanceHistory.service_date <= date_to)
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        search_conditions = [
            MaintenanceHistory.part_type_id.ilike(pattern),
            MaintenanceHistory.notes.ilike(pattern),
        ]
        # O nome da peça não fica no banco; traduzimos o termo para os
        # ids correspondentes do catálogo para permitir busca por nome.
        matched_ids = matching_part_ids(search)
        if matched_ids:
            search_conditions.append(MaintenanceHistory.part_type_id.in_(matched_ids))
        conditions.append(or_(*search_conditions))

    total = db.scalar(
        select(func.count()).select_from(MaintenanceHistory).where(*conditions)
    ) or 0
    ordering = (
        MaintenanceHistory.service_date.asc()
        if order == "asc"
        else MaintenanceHistory.service_date.desc()
    )
    records = db.scalars(
        select(MaintenanceHistory)
        .where(*conditions)
        .order_by(ordering, MaintenanceHistory.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return MaintenanceHistoryPage(
        items=[history_item(record) for record in records],
        total=int(total),
        limit=limit,
        offset=offset,
    )


@router.get(
    "/cars/{car_id}/maintenance-history",
    response_model=MaintenanceHistoryPage,
    summary="Busca o histórico de manutenções de um carro",
)
def car_maintenance_history(
    car_id: str,
    part_id: str | None = Query(default=None, description="Filtra por id da peça"),
    part_type_id: str | None = Query(default=None, description="Filtra pelo tipo da peça"),
    date_from: date | None = Query(default=None, description="Data inicial do serviço"),
    date_to: date | None = Query(default=None, description="Data final do serviço"),
    search: str | None = Query(default=None, max_length=120, description="Busca por peça ou observação"),
    order: Literal["asc", "desc"] = Query(default="desc", description="Ordenação por data do serviço"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna o histórico paginado e filtrado de um carro do usuário.

    Requer o token JWT no cabeçalho ``Authorization: Bearer <token>``.
    Carros de outros usuários retornam ``404`` para não revelar sua existência.
    """

    return maintenance_history_page(
        db,
        user,
        car_id=car_id,
        part_id=part_id,
        part_type_id=part_type_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        order=order,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/maintenance-history",
    response_model=MaintenanceHistoryPage,
    summary="Busca o histórico de manutenções de todos os carros do usuário",
)
def all_maintenance_history(
    car_id: str | None = Query(default=None, description="Restringe a busca a um carro"),
    part_id: str | None = Query(default=None, description="Filtra por id da peça"),
    part_type_id: str | None = Query(default=None, description="Filtra pelo tipo da peça"),
    date_from: date | None = Query(default=None, description="Data inicial do serviço"),
    date_to: date | None = Query(default=None, description="Data final do serviço"),
    search: str | None = Query(default=None, max_length=120, description="Busca por peça ou observação"),
    order: Literal["asc", "desc"] = Query(default="desc", description="Ordenação por data do serviço"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Busca autenticada em todo o histórico do usuário.

    Aceita os mesmos filtros do endpoint por carro e pode ser restringida
    com o parâmetro opcional ``car_id``.
    """

    return maintenance_history_page(
        db,
        user,
        car_id=car_id,
        part_id=part_id,
        part_type_id=part_type_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        order=order,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/cars/{car_id}/deadline-chart",
    summary="Gera um gráfico PNG com os prazos do carro",
    responses={200: {"content": {"image/png": {}}}},
)
def car_deadline_chart(
    car_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gera, com Matplotlib, um gráfico dos prazos das peças do carro.

    O gráfico usa barras horizontais com a quantidade de dias até o
    vencimento. Cores: vermelho (vencido), âmbar (vence em até 45 dias)
    e verde (em dia). Requer autenticação e propriedade do carro.
    """

    car = owned_car(db, user, car_id)
    parts = (
        db.scalars(select(Part).where(Part.id.in_(car.parts_ids or []))).all()
        if car.parts_ids
        else []
    )
    if not car_deadlines(parts, float(car.weekly_usage or 0)):
        raise HTTPException(
            status_code=404,
            detail="No parts with known maintenance intervals",
        )
    image = render_deadline_chart(car, parts, float(car.weekly_usage or 0))
    return Response(
        content=image,
        media_type="image/png",
        headers={"Content-Disposition": f'inline; filename="prazos-{car.id}.png"'},
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
    # O histórico pertence ao carro e deve ser removido junto com ele.
    db.execute(delete(MaintenanceHistory).where(MaintenanceHistory.car_id == car.id))
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
    # Toda peça adicionada começa com um evento no histórico.
    record_maintenance(db, car, part, part.last_maintenance)
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
    new_service_date = payload.maintenance_date()
    # Só registra um novo evento quando a data realmente muda; isso evita
    # duplicar o histórico caso o frontend reenvie a mesma data.
    if new_service_date != part.last_maintenance:
        record_maintenance(db, car, part, new_service_date)
    part.last_maintenance = new_service_date
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

def send_email(receiver: str, subject: str, body: str):
    sender = "suporte.manutencar@gmail.com"
    password_app = "sua_senha_de_app_do_gmail" # move pro o get_settings() depois
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password_app)
            server.sendmail(sender, receiver, msg.as_string())
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# CADASTRO
@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user_exists = db.scalar(select(User).where(User.email == payload.email))
    if user_exists:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    
    new_user = User(
        id=str(uuid4()),
        email=payload.email,
        password_hash=hash_password(payload.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return user_response(new_user)

# RECUPERAÇÃO DE ACESSO
@router.post("/auth/recover")
def recover_password(payload: EmailRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if user:
        settings = get_settings()
        token = jwt.encode({"sub": user.email, "exp": datetime.utcnow() + timedelta(minutes=15)}, settings.jwt_secret, algorithm="HS256")
        link = f"https://manutencar.com.br/redefinir?token={token}"
        send_email(user.email, "ManutenCar - Redefinição", f"Link: {link}")
    return {"message": "Se o e-mail existir, um link foi enviado."}

# SOLICITAÇÃO DE EXCLUSÃO LGPD
@router.post("/auth/delete-request")
def request_deletion(user: User = Depends(get_current_user)):
    settings = get_settings()
    token = jwt.encode({"sub": user.email, "action": "delete", "exp": datetime.utcnow() + timedelta(minutes=15)}, settings.jwt_secret, algorithm="HS256")
    link = f"https://manutencar.com.br/excluir?token={token}"
    send_email(user.email, "ManutenCar - Confirmação de Exclusão", f"Confirme a exclusão irreversível (LGPD): {link}")
    return {"message": "E-mail de validação enviado."}

# CONFIRMAÇÃO DE EXCLUSÃO LGPD
@router.post("/auth/delete-confirm")
def confirm_deletion(payload: TokenConfirm, db: Session = Depends(get_db)):
    settings = get_settings()
    try:
        decoded = jwt.decode(payload.token, settings.jwt_secret, algorithms=["HS256"])
        if decoded.get("action") != "delete":
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    
    user = db.scalar(select(User).where(User.email == decoded["sub"]))
    if user:
        # remove e-mail e senha, inativa o acesso
        user.email = f"deleted_{user.id}@manutencar.local"
        user.password_hash = "deleted"
        db.commit()
    return {"message": "Conta removida segundo a LGPD."}
