"""Catálogo de peças e intervalos de manutenção.

O frontend mantém o mesmo catálogo em ``src/data/parts.ts``. O backend
precisa conhecer esses intervalos para calcular os prazos e gerar os
gráficos com Matplotlib, já que o banco armazena apenas o ``part_type_id``.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PartSpec:
    """Especificação estática de um tipo de peça."""

    id: str
    name: str
    interval_km: int
    interval_months: int
    category: str
    color: str


CATALOG: dict[str, PartSpec] = {
    spec.id: spec
    for spec in (
        PartSpec("engine-oil", "Engine oil & filter", 10000, 12, "Engine", "orange"),
        PartSpec("air-filter", "Engine air filter", 20000, 24, "Engine", "blue"),
        PartSpec("cabin-filter", "Cabin air filter", 15000, 12, "Comfort", "green"),
        PartSpec("brake-fluid", "Brake fluid", 40000, 24, "Brakes", "red"),
        PartSpec("brake-pads", "Brake pads", 40000, 36, "Brakes", "purple"),
        PartSpec("spark-plugs", "Spark plugs", 40000, 36, "Engine", "yellow"),
        PartSpec("coolant", "Coolant", 40000, 36, "Fluids", "teal"),
        PartSpec("timing-belt", "Timing belt", 100000, 60, "Engine", "pink"),
        PartSpec("battery", "Battery", 60000, 48, "Electrical", "slate"),
    )
}


def get_part(part_type_id: str) -> PartSpec | None:
    """Retorna a especificação da peça ou ``None`` se o tipo for desconhecido."""

    return CATALOG.get(part_type_id)


def part_name(part_type_id: str, fallback: str | None = None) -> str:
    """Retorna o nome legível da peça, usando o id como fallback."""

    spec = get_part(part_type_id)
    return spec.name if spec else (fallback or part_type_id)


def matching_part_ids(term: str) -> list[str]:
    """Lista ids de peças cujo id ou nome contenha o termo pesquisado.

    Usado pelo filtro ``search`` do histórico para permitir que o usuário
    encontre registros pelo nome da peça, mesmo o nome não estando no banco.
    """

    needle = term.strip().lower()
    if not needle:
        return []
    return [
        spec.id
        for spec in CATALOG.values()
        if needle in spec.id.lower() or needle in spec.name.lower()
    ]
