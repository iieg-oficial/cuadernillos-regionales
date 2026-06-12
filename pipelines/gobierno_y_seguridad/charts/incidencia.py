from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import squarify

from core.constants import COLOR_GRIS, COLOR_SECCION, COLOR_TEXTO

MESES_CORTOS = {
    1: "ene",
    2: "feb",
    3: "mar",
    4: "abr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dic",
}

COLORES_BIENES = [
    "#5C2472",
    "#7A4A8A",
    "#E88A2A",
    "#C75B12",
    "#9B59B6",
    "#D4A5E5",
    "#E6772E",
]


def grafica_carpetas_por_mes(
    carpetas_por_mes,
    municipio,
    output_path: Path,
):
    datos = sorted(carpetas_por_mes, key=lambda r: (r["anio"], r["mes"]))
    etiquetas = [f"{MESES_CORTOS[r['mes']]}-{r['anio']}" for r in datos]
    valores = [r["total"] for r in datos]
    media = sum(valores) / len(valores)

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        etiquetas,
        valores,
        color=COLOR_SECCION,
        linewidth=2.5,
        marker="o",
        markersize=7,
        markerfacecolor="white",
        markeredgecolor=COLOR_SECCION,
        markeredgewidth=2,
        zorder=3,
    )

    for i, (x, val) in enumerate(zip(etiquetas, valores)):
        ax.annotate(
            f"{val:,}".replace(",", " "),
            (x, val),
            textcoords="offset points",
            xytext=(0, 12),
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=COLOR_TEXTO,
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="white",
                edgecolor=COLOR_SECCION,
                linewidth=0.8,
            ),
        )

    media_label = f"Media = {media:,.0f}".replace(",", " ")
    ax.axhline(
        y=media,
        color=COLOR_GRIS,
        linestyle="--",
        linewidth=1.2,
        zorder=1,
    )
    ax.text(
        len(etiquetas) - 0.5,
        media,
        f"  {media_label}",
        ha="left",
        va="bottom",
        fontsize=8,
        color=COLOR_GRIS,
        style="italic",
    )

    ax.set_ylabel("Carpetas", fontsize=11, color=COLOR_TEXTO)
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", " "))
    )

    y_min = min(valores) * 0.9
    y_max = max(valores) * 1.12
    ax.set_ylim(y_min, y_max)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_TEXTO)
    ax.spines["bottom"].set_color(COLOR_TEXTO)
    ax.tick_params(colors=COLOR_TEXTO, labelsize=9)
    plt.xticks(rotation=45, ha="right")

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def grafica_bienes_juridicos(
    casos_bien_afectado,
    municipio,
    output_path: Path,
):
    total = sum(r["total"] for r in casos_bien_afectado)
    datos = []
    for r in casos_bien_afectado:
        pct = r["total"] / total * 100
        nombre = r["bien_afectado"]
        if nombre.startswith("Otros bienes"):
            nombre = "Otros bienes jurídicos"
        datos.append({"nombre": nombre, "pct": pct})

    nombres = [d["nombre"] for d in datos]
    valores = [d["pct"] for d in datos]
    colores = COLORES_BIENES[: len(datos)]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")

    squarify.plot(
        sizes=valores,
        label=None,
        color=colores,
        alpha=1.0,
        ax=ax,
        pad=False,
    )

    rects = [
        c
        for c in ax.get_children()
        if isinstance(c, plt.Rectangle) and c.get_width() > 0
    ]
    rects = rects[: len(datos)]

    for rect, dato in zip(rects, datos):
        x = rect.get_x() + rect.get_width() / 2
        y = rect.get_y() + rect.get_height() / 2
        pct_text = f"{dato['pct']:.1f} %"
        rw = rect.get_width()
        rh = rect.get_height()
        if rw < 5 or rh < 4:
            fontsize = 5
        elif dato["pct"] > 15:
            fontsize = 14
        elif dato["pct"] > 5:
            fontsize = 10
        else:
            fontsize = 7
        ax.text(
            x,
            y,
            pct_text,
            ha="center",
            va="center",
            fontsize=fontsize,
            fontweight="bold",
            color="white",
        )

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c) for c in colores]
    ax.legend(
        handles,
        nombres,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.11),
        ncol=3,
        fontsize=8,
        frameon=False,
    )

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def grafica_principales_delitos(
    casos_por_delito,
    bien_principal,
    municipio,
    output_path: Path,
):
    top = casos_por_delito[:5]
    nombres = [r["delito"] for r in top]
    valores = [r["total"] for r in top]

    colores = [COLOR_SECCION] + [COLOR_GRIS] * (len(top) - 1)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(range(len(top)), valores, color=colores, width=0.7, edgecolor="none")

    for bar, val in zip(bars, valores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{val:,}".replace(",", " "),
            ha="center",
            va="bottom",
            fontsize=10,
            color=COLOR_TEXTO,
            fontweight="bold",
        )

    wrapped = []
    for n in nombres:
        words = n.split()
        lines = []
        current = ""
        for w in words:
            if current and len(current + " " + w) > 15:
                lines.append(current)
                current = w
            else:
                current = current + " " + w if current else w
        if current:
            lines.append(current)
        wrapped.append("\n".join(lines))

    ax.set_xticks(range(len(top)))
    ax.set_xticklabels(wrapped, fontsize=9, color=COLOR_TEXTO)
    ax.set_xlabel("Subtipos de delitos", fontsize=11, color=COLOR_TEXTO)
    ax.set_ylabel("Carpetas", fontsize=11, color=COLOR_TEXTO)
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", " "))
    )
    ax.set_ylim(0, max(valores) * 1.15)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_TEXTO)
    ax.spines["bottom"].set_color(COLOR_TEXTO)
    ax.tick_params(colors=COLOR_TEXTO)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path
