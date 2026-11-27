from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class MaintenanceStatus(str, Enum):
    OVERDUE = "overdue"
    SOON = "soon"
    ON_TRACK = "on-track"


@dataclass(frozen=True, slots=True)
class MaintenanceDeadline:
    label: str
    days_until: int

    @property
    def status(self) -> MaintenanceStatus:
        if self.days_until < 0:
            return MaintenanceStatus.OVERDUE
        if self.days_until <= 45:
            return MaintenanceStatus.SOON
        return MaintenanceStatus.ON_TRACK


STATUS_COLORS = {
    MaintenanceStatus.OVERDUE: "#DC2626",
    MaintenanceStatus.SOON: "#DC2626",
    MaintenanceStatus.ON_TRACK: "#16A34A",
}


def render_deadline_chart(deadlines: Iterable[MaintenanceDeadline]) -> BytesIO:
    items = list(deadlines)
    height = max(3.0, 0.62 * len(items) + 1.8)
    figure, axis = plt.subplots(figsize=(10, height), constrained_layout=True)
    figure.patch.set_facecolor("#FFFFFF")
    axis.set_facecolor("#FFFFFF")

    if not items:
        axis.text(
            0.5, 0.5, "No tracked maintenance deadlines",
            ha="center", va="center", color="#475569", fontsize=11,
            transform=axis.transAxes,
        )
        axis.set_axis_off()
    else:
        labels = [item.label for item in items]
        values = [item.days_until for item in items]
        colors = [STATUS_COLORS[item.status] for item in items]
        positions = list(range(len(items)))
        axis.barh(positions, values, color=colors, height=0.62, zorder=3)
        axis.set_yticks(positions, labels)
        axis.invert_yaxis()
        axis.axvline(0, color="#F36808", linewidth=1.5, zorder=2)
        axis.set_xlabel("Days until service (negative values are overdue)", color="#475569")
        axis.set_title("Maintenance deadlines", loc="left", color="#14325C", fontsize=15, weight="bold", pad=14)
        axis.xaxis.grid(True, color="#DCE3EC", linewidth=0.8, zorder=0)
        axis.tick_params(axis="y", length=0, labelcolor="#14325C", labelsize=10)
        axis.tick_params(axis="x", colors="#475569", labelsize=9)
        for spine in axis.spines.values():
            spine.set_visible(False)
        low, high = min(0, min(values)), max(0, max(values))
        span = max(high - low, 1)
        axis.set_xlim(low - span * 0.15, high + span * 0.2)
        for position, item in zip(positions, items):
            value = item.days_until
            label = f"{abs(value)}d overdue" if value < 0 else f"{value}d"
            offset = -span * 0.025 if value < 0 else span * 0.025
            axis.text(
                value + offset, position, label,
                ha="right" if value < 0 else "left", va="center",
                color="#14325C", fontsize=8,
            )

    output = BytesIO()
    try:
        figure.savefig(output, format="png", dpi=220, bbox_inches="tight", facecolor=figure.get_facecolor())
    finally:
        plt.close(figure)
    output.seek(0)
    return output
