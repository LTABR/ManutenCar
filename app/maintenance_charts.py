"""PNG charts for the maintenance deadlines shown by the planner.

The planner estimates the next service date from the earlier of its calendar
and mileage dates. It marks a service overdue when that date has passed, due
soon when it falls within 45 days, and on track otherwise. ``days_until``
should be computed from that estimated date by the caller.
"""

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
    """Traffic-light states used by the maintenance planner."""

    OVERDUE = "overdue"
    SOON = "soon"
    ON_TRACK = "on-track"


@dataclass(frozen=True, slots=True)
class MaintenanceDeadline:
    """A maintenance item and days remaining until its next service."""

    label: str
    days_until: int

    @property
    def status(self) -> MaintenanceStatus:
        if self.days_until < 0:
            return MaintenanceStatus.OVERDUE
        if self.days_until <= 45:
            return MaintenanceStatus.SOON
        return MaintenanceStatus.ON_TRACK


_STATUS_COLORS: dict[MaintenanceStatus, str] = {
    MaintenanceStatus.OVERDUE: "#dc2626",
    MaintenanceStatus.SOON: "#d99a0b",
    MaintenanceStatus.ON_TRACK: "#16a34a",
}


def _build_deadline_figure(deadlines: list[MaintenanceDeadline]) -> Figure:
    height = max(2.8, 0.55 * len(deadlines) + 1.7)
    figure, axis = plt.subplots(figsize=(9, height), constrained_layout=True)
    figure.patch.set_facecolor("#ffffff")
    axis.set_facecolor("#ffffff")

    if not deadlines:
        axis.text(
            0.5,
            0.5,
            "No maintenance deadlines to display",
            ha="center",
            va="center",
            color="#64748b",
            fontsize=11,
            transform=axis.transAxes,
        )
        axis.set_axis_off()
        return figure

    labels = [deadline.label for deadline in deadlines]
    values = [deadline.days_until for deadline in deadlines]
    colors = [_STATUS_COLORS[deadline.status] for deadline in deadlines]
    positions = list(range(len(deadlines)))

    axis.barh(positions, values, color=colors, height=0.62, zorder=3)
    axis.set_yticks(positions, labels)
    axis.invert_yaxis()
    axis.axvline(0, color="#475569", linewidth=1, zorder=2)
    axis.set_xlabel("Days until service (negative values are overdue)", color="#475569")
    axis.set_title("Maintenance deadlines", loc="left", color="#0f172a", fontsize=14, weight="bold", pad=14)
    axis.xaxis.grid(True, color="#e2e8f0", linewidth=0.8, zorder=0)
    axis.tick_params(axis="y", length=0, labelcolor="#334155", labelsize=9)
    axis.tick_params(axis="x", colors="#64748b", labelsize=9)
    for spine in axis.spines.values():
        spine.set_visible(False)

    low, high = min(0, min(values)), max(0, max(values))
    span = max(high - low, 1)
    axis.set_xlim(low - span * 0.15, high + span * 0.2)
    for position, deadline in zip(positions, deadlines):
        value = deadline.days_until
        label = f"{abs(value)}d overdue" if value < 0 else f"{value}d"
        offset = -span * 0.025 if value < 0 else span * 0.025
        axis.text(
            value + offset,
            position,
            label,
            ha="right" if value < 0 else "left",
            va="center",
            color="#334155",
            fontsize=8,
        )

    return figure


def render_deadline_chart(deadlines: Iterable[MaintenanceDeadline]) -> BytesIO:
    """Render a traffic-light deadline chart as a rewound PNG buffer."""

    figure = _build_deadline_figure(list(deadlines))
    output = BytesIO()
    try:
        figure.savefig(output, format="png", dpi=160, bbox_inches="tight")
    finally:
        plt.close(figure)
    output.seek(0)
    return output


def render_deadline_chart_bytes(deadlines: Iterable[MaintenanceDeadline]) -> bytes:
    """Render a deadline chart as PNG bytes for an API response."""

    return render_deadline_chart(deadlines).getvalue()
