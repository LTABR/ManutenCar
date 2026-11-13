from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    email: str
    password: str

class EmailRequest(BaseModel):
    email: str

class TokenConfirm(BaseModel):
    token: str

class EncryptedLogin(BaseModel):
    algorithm: str = Field(pattern=r"^RSA-OAEP-256\+A256GCM$")
    encryptedKey: str
    iv: str
    ciphertext: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

class LoginResponse(BaseModel):
    accessToken: str
    user: UserResponse

class PartResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    partId: str
    lastServiced: date

class CarCreate(BaseModel):
    brand: str = ""
    model: str = ""
    weekly_usage: float = Field(default=0, ge=0)
    distance: str | None = None
    frequency: str = "week"

    def weekly_km(self) -> float:
        if self.distance is None:
            return self.weekly_usage
        try:
            distance = max(float(self.distance), 0)
        except (TypeError, ValueError):
            return 0
        return {"week": distance, "month": distance * 12 / 52, "year": distance / 52}.get(self.frequency, distance)

class CarUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    weekly_usage: float | None = Field(default=None, ge=0)
    distance: str | None = None
    frequency: str | None = None

class PartCreate(BaseModel):
    id: str | None = None
    part_type_id: str | None = None
    partId: str | None = None
    last_maintenance: date | None = None
    lastServiced: date | None = None

    def type_id(self) -> str:
        return self.part_type_id or self.partId or ""

    def maintenance_date(self) -> date:
        return self.last_maintenance or self.lastServiced or date.today()

class PartUpdate(BaseModel):
    last_maintenance: date | None = None
    lastServiced: date | None = None

    def maintenance_date(self) -> date:
        return self.last_maintenance or self.lastServiced or date.today()

class CarResponse(BaseModel):
    id: str
    brand: str
    model: str
    owners_ids: list[str]
    parts_ids: list[str]
    weekly_usage: float
    distance: str
    frequency: str
    parts: list[dict[str, Any]]


class MaintenanceHistoryItem(BaseModel):
    """Item retornado pela busca de histórico de manutenções."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    car_id: str
    part_id: str | None = None
    part_type_id: str
    part_name: str
    service_date: date
    mileage: float | None = None
    notes: str | None = None
    created_at: datetime


class MaintenanceHistoryPage(BaseModel):
    """Resposta paginada da busca de histórico."""

    items: list[MaintenanceHistoryItem]
    total: int
    limit: int
    offset: int
