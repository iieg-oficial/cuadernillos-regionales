from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

COLOR_SECCION = "#5C2472"
COLOR_GRIS = "#B0B0B0"
COLOR_TEXTO = "#465055"
N_ANIOS = 6


def grafica_produccion(
    datos: list[dict],
    municipio: str,
    tipo: str,
    output_path: Path,
):
    ultimos = datos[-N_ANIOS:]
    anios = [str(d["anio"]) for d in ultimos]
    valores = [d["valor_miles"] for d in ultimos]

    colores = [COLOR_GRIS] * len(anios)
    colores[-1] = COLOR_SECCION

    fig, ax = plt.subplots(figsize=(10, 5.5))

    bars = ax.bar(anios, valores, color=colores, width=0.85, edgecolor="none")

    for bar, val in zip(bars, valores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{val:,.2f}".replace(",", " "),
            ha="center",
            va="bottom",
            fontsize=10,
            color=COLOR_TEXTO,
            fontweight="bold",
        )

    ax.set_xlabel("Año", fontsize=11, color=COLOR_TEXTO)
    ax.set_ylabel("Valor de la producción", fontsize=11, color=COLOR_TEXTO)
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
