from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from core.constants import COLOR_TEXTO
from core.utils.charts import setup_chart_style

DPI = 300
AXIS_COLOR = "#9CA3AF"
TEXT_COLOR = COLOR_TEXTO
LIGHT_GRID = "#E5E7EB"
MONTH_LABELS = [
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
]
MONTH_ORDER = [
    "ENE",
    "FEB",
    "MAR",
    "ABR",
    "MAY",
    "JUN",
    "JUL",
    "AGO",
    "SEP",
    "OCT",
    "NOV",
    "DIC",
]


def _setup_style():
    setup_chart_style()


def _save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.02, transparent=True)
    plt.close(fig)


def _monthly_data(long_rows):
    by_periodo = {}
    for row in long_rows:
        periodo = str(row.get("periodo", "")).upper().strip()
        if periodo in MONTH_ORDER:
            by_periodo[periodo] = row
    ordered = []
    for m in MONTH_ORDER:
        if m in by_periodo:
            ordered.append(by_periodo[m])
    return ordered


def plot_temperatura(long_rows, output_path):
    _setup_style()
    data = _monthly_data(long_rows)
    if len(data) < 12:
        return

    x = np.arange(len(data))
    means = np.array([float(r.get("mean", 0) or 0) for r in data])
    mins = np.array([float(r.get("min", 0) or 0) for r in data])
    maxs = np.array([float(r.get("max", 0) or 0) for r in data])

    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    ax.fill_between(x, mins, maxs, color="#D8B5E8", alpha=0.28, linewidth=0)
    ax.plot(
        x,
        means,
        color="#FF8300",
        linewidth=2.6,
        marker="o",
        markersize=5.5,
        markeredgewidth=0,
    )
    for xp, val in zip(x, means):
        ax.text(
            xp,
            val + 0.35,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=TEXT_COLOR,
        )
    ax.set_ylabel("°C", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(MONTH_LABELS, fontsize=12, fontweight="bold")
    ax.yaxis.grid(True, color=LIGHT_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    for label in ax.get_yticklabels():
        label.set_fontsize(12)
        label.set_fontweight("bold")
    fig.subplots_adjust(left=0.075, right=0.985, top=0.93, bottom=0.13)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    _save(fig, output_path)


def plot_precipitacion(long_rows, output_path):
    _setup_style()
    data = _monthly_data(long_rows)
    if len(data) < 12:
        return

    x = np.arange(len(data))
    mins = np.array([float(r.get("min", 0) or 0) for r in data])
    maxs = np.array([float(r.get("max", 0) or 0) for r in data])
    means = np.array([float(r.get("mean", 0) or 0) for r in data])

    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    w = 0.23
    ax.bar(x - w, mins, color="#8F39B1", edgecolor="none", width=w, label="Mínimo")
    ax.bar(x, means, color="#FF8300", edgecolor="none", width=w, label="Media")
    ax.bar(x + w, maxs, color="#622484", edgecolor="none", width=w, label="Máximo")
    ax.set_ylabel("mm", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(MONTH_LABELS, fontsize=12, fontweight="bold")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.07),
        ncol=3,
        frameon=False,
        fontsize=8.5,
    )
    ax.yaxis.grid(True, color=LIGHT_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    for label in ax.get_yticklabels():
        label.set_fontsize(12)
        label.set_fontweight("bold")
    fig.subplots_adjust(left=0.075, right=0.985, top=0.94, bottom=0.18)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    _save(fig, output_path)


def plot_vientos(wind_data, output_path):
    _setup_style()
    grade_cols = sorted(
        [k for k in wind_data if k.startswith("grado_")],
        key=lambda k: int(k.split("_")[1]),
    )
    if not grade_cols:
        return

    angles_deg = [int(k.split("_")[1]) for k in grade_cols]
    theta = np.deg2rad(angles_deg)
    values = np.array([float(wind_data.get(k, 0) or 0) for k in grade_cols])

    if np.nansum(values) <= 0:
        return

    max_val = float(np.nanmax(values))
    colors = ["#FF8300" if v == max_val else "#8F39B1" for v in values]

    fig = plt.figure(figsize=(5.2, 5.2))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.bar(
        theta,
        values,
        width=np.deg2rad(26),
        bottom=0.0,
        color=colors,
        edgecolor="none",
        linewidth=0,
        alpha=0.95,
    )
    ax.set_xticks(np.deg2rad([0, 90, 180, 270]))
    ax.set_xticklabels(["N", "E", "S", "O"], fontsize=12, fontweight="bold")
    radial_max = max(max_val * 1.12, 0.05)
    ax.set_ylim(0, radial_max)
    ax.set_yticks(np.linspace(radial_max / 4, radial_max, 4))
    ax.set_yticklabels([])
    ax.grid(True, axis="x", linestyle="--", alpha=0.30, color=AXIS_COLOR)
    ax.grid(True, axis="y", linestyle="-", alpha=0.22, color=AXIS_COLOR)
    ax.spines["polar"].set_color(AXIS_COLOR)

    for angle, val in zip(theta, values):
        if val < 0.05:
            continue
        fontsize = min(8, max(4.5, 4 + (val / max_val) * 4))
        ax.text(
            angle,
            val * 0.78,
            f"{val * 100:.2f} %",
            ha="center",
            va="center",
            fontsize=fontsize,
            fontweight="bold",
            color="white",
        )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.02, transparent=False)
    plt.close(fig)
