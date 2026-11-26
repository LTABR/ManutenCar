from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class EncryptedAuthPayload(BaseModel):
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
    part_type_id: str | None = Field(default=None, max_length=80)
    partId: str | None = Field(default=None, max_length=80)
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


class SupportTicketCreate(BaseModel):
    category: Literal["Account/Login", "Vehicle & Maintenance Calculations", "System Bug", "General Question"]
    subject: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=4000)


class SupportTicketResponse(BaseModel):
    id: str
    category: str
    subject: str
    description: str
    status: str
    created_at: datetime


class MaintenanceHistoryItem(BaseModel):
    id: str
    vehicle_id: str
    part_id: str | None
    part_name: str | None
    service_date: date
    title: str
    description: str | None
    category: str | None
    status: str | None


class MaintenanceHistoryResponse(BaseModel):
    items: list[MaintenanceHistoryItem]
    total: int
    page: int
    page_size: int


class MaintenanceDeadlineRequestItem(BaseModel):
    label: str = Field(max_length=120)
    days_until: int


class MaintenanceDeadlinesRequest(BaseModel):
    deadlines: list[MaintenanceDeadlineRequestItem] = Field(max_length=100)


class MaintenanceDeadlineResponse(BaseModel):
    part_id: str
    last_serviced: date | None
    due_date: date | None
    days_until: int | None
    status: Literal["untracked", "on-track", "soon", "overdue"]
