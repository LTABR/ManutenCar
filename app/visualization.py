"""Geração dos gráficos de prazos com Matplotlib.

Usamos o backend ``Agg`` e a API de ``Figure`` (sem ``pyplot``) para que a
geração de imagens funcione em servidores sem interface gráfica e não sofra
com estado global compartilhado entre requisições.
"""

from datetime import date
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from .deadlines import Deadline, car_deadlines  # noqa: E402
from .models import Car, Part  # noqa: E402

_STATUS_COLORS = {
    "overdue": "#c0392b",
    "soon": "#d68910",
    "on-track": "#1e8449",
}
_STATUS_LABELS = {
    "overdue": "Vencido",
    "soon": "Próximo (até 45 dias)",
    "on-track": "Em dia",
}


def _car_label(car: Car) -> str:
    """Monta um título legível para o carro."""

    description = " ".join(value for value in (car.brand, car.model) if value).strip()
    return description or f"Carro {car.id[:8]}"


def _bar_annotation(deadline: Deadline) -> str:
    """Texto exibido ao lado de cada barra do gráfico."""

    if deadline.days_until < 0:
        return f"{abs(deadline.days_until)} dia(s) de atraso"
    if deadline.days_until == 0:
        return "vence hoje"
    return f"em {deadline.days_until} dia(s)"


def render_deadline_chart(
    car: Car,
    parts: list[Part],
    weekly_usage: float,
    today: date | None = None,
) -> bytes:
    """Gera um PNG com os prazos das peças do carro.

    Cada barra representa a quantidade de dias até o próximo vencimento.
    Barras negativas indicam manutenções atrasadas. A cor segue o status:
    vermelho (vencido), âmbar (próximo) e verde (em dia).
    """

    deadlines = car_deadlines(parts, weekly_usage, today)
    figure = Figure(
        figsize=(10, max(3.2, 0.65 * len(deadlines) + 2.0)),
        dpi=150,
        facecolor="white",
    )
    FigureCanvasAgg(figure)
    axes = figure.add_subplot(111)

    if not deadlines:
        axes.axis("off")
        axes.text(
            0.5,
            0.5,
            "Nenhuma peça com intervalo de manutenção conhecido.",
            ha="center",
            va="center",
            fontsize=12,
            color="#4a4a4a",
        )
        buffer = BytesIO()
        figure.savefig(buffer, format="png", bbox_inches="tight", facecolor="white")
        return buffer.getvalue()

    labels = [
        f"{deadline.part_name}\n{deadline.next_due:%d/%m/%Y}"
        for deadline in deadlines
    ]
    values = [deadline.days_until for deadline in deadlines]
    colors = [_STATUS_COLORS[deadline.status] for deadline in deadlines]

    bars = axes.barh(labels, values, color=colors, edgecolor="#2c3e50", linewidth=0.4)
    axes.axvline(0, color="#2c3e50", linewidth=1.0, linestyle="--")
    axes.invert_yaxis()
    axes.set_xlabel("Dias até o vencimento (valores negativos = atrasado)")
    axes.set_title(
        f"Prazos de manutenção — {_car_label(car)}",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    axes.grid(axis="x", color="#d5d8dc", linewidth=0.6, alpha=0.8)
    axes.set_axisbelow(True)

    for bar, deadline in zip(bars, deadlines, strict=True):
        width = bar.get_width()
        # Para barras negativas (atrasadas), ancoramos o texto no zero para
        # não invadir os nomes das peças no eixo vertical.
        anchor_x = width if width >= 0 else 0
        axes.annotate(
            _bar_annotation(deadline),
            xy=(anchor_x, bar.get_y() + bar.get_height() / 2),
            xytext=(4, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=8,
            color="#2c3e50",
        )

    present_statuses = {deadline.status for deadline in deadlines}
    handles = [
        Patch(color=_STATUS_COLORS[status], label=_STATUS_LABELS[status])
        for status in ("overdue", "soon", "on-track")
        if status in present_statuses
    ]
    axes.legend(handles=handles, loc="upper right", frameon=False, fontsize=8)

    buffer = BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight", facecolor="white")
    return buffer.getvalue()
