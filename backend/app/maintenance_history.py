from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .models import MaintenanceRecord, Part


def query_maintenance_history(
    db: Session,
    vehicle_id: str,
    *,
    keyword: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    category: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[tuple[MaintenanceRecord, str | None]], int]:
    filters = [MaintenanceRecord.vehicle_id == vehicle_id]
    if start_date:
        filters.append(MaintenanceRecord.service_date >= start_date)
    if end_date:
        filters.append(MaintenanceRecord.service_date <= end_date)
    if category:
        filters.append(func.lower(MaintenanceRecord.category) == category.strip().lower())
    if status:
        filters.append(func.lower(MaintenanceRecord.status) == status.strip().lower())
    if keyword and keyword.strip():
        pattern = f"%{keyword.strip().lower()}%"
        filters.append(
            or_(
                func.lower(MaintenanceRecord.title).like(pattern),
                func.lower(func.coalesce(MaintenanceRecord.description, "")).like(pattern),
                func.lower(func.coalesce(Part.part_type_id, "")).like(pattern),
            )
        )

    matching = (
        select(MaintenanceRecord.id)
        .outerjoin(Part, Part.id == MaintenanceRecord.part_id)
        .where(*filters)
    )
    total = db.scalar(select(func.count()).select_from(matching.subquery())) or 0
    rows = db.execute(
        select(MaintenanceRecord, Part.part_type_id)
        .outerjoin(Part, Part.id == MaintenanceRecord.part_id)
        .where(*filters)
        .order_by(MaintenanceRecord.service_date.desc(), MaintenanceRecord.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [(record, part_name) for record, part_name in rows], total
