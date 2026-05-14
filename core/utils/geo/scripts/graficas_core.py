#!/usr/bin/env python3
"""
Flujo centralizado para generar graficas de los Cuadernillos Municipales IIEG 2026.

Lee tablas *_estadistica_detalle.csv desde la carpeta centralizada de resultados,
genera PNG por municipio y guarda las salidas en subcarpetas por tema.
"""

from __future__ import annotations

import argparse
import csv
import logging
import math
import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.patches import Patch, Rectangle


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = PROJECT_ROOT / "datos_estadisticos"
OUTPUT_ROOT = PROJECT_ROOT / "graficas"
LOG_PATH = OUTPUT_ROOT / "resumen_graficas.csv"
WIND_CSV = RESULTS_ROOT / "global_wind_frecuencia_municipal.csv"

TRANSPARENT_BG = True
DPI = 300
FONT_FAMILY = "Lexend"
FALLBACK_FONT = "DejaVu Sans"

EXCLUDED_TOPICS = {
    "anp_humedales_manglares": "Tema omitido por solicitud: ANP.",
    "salud_nivel_atencion": "Tema omitido por solicitud: Salud.",
    "educacion_nivel": "Tema omitido por solicitud: Educacion.",
    "espacios_publicos": "Tema omitido por solicitud: Espacios publicos.",
    "energia": "Tema omitido por solicitud: Energias.",
}

CHART_STYLE = {
    "figsize_proportion": (10.4, 3.75),
    "figsize_stacked": (10.4, 2.85),
    "treemap_height": 46,
    "treemap_label_area_min": 0.055,
    "treemap_label_width_min": 11,
    "treemap_label_height_min": 7,
    "wind_height_tex": r"0.31\textheight",
}

COLOR_PALETTE = {
    "orange": "#FF8300",
    "orange_base": "#FA8524",
    "orange_dark_01": "#8F3A0B",
    "orange_dark_02": "#B95712",
    "orange_mid_01": "#D66A18",
    "orange_mid_02": "#E87722",
    "orange_mid_03": "#F07A1E",
    "peach_01": "#FF9A4A",
    "peach_02": "#FFA35C",
    "peach_03": "#FFAE70",
    "peach_04": "#FFB678",
    "peach_05": "#FFC185",
    "peach_06": "#FFC894",
    "peach_07": "#FFD0A3",
    "peach_08": "#FFD8AE",
    "peach_09": "#FFE0BD",
    "peach_10": "#FFE4C6",
    "peach_11": "#FFEAD1",
    "peach_12": "#FFF0DD",

    "purple_01": "#EACEF6",
    "purple_02": "#DDB3EF",
    "purple_03": "#CF98E6",
    "purple_04": "#BF7DDB",
    "purple_05": "#AD63CE",
    "purple_06": "#9B4DBF",
    "purple_07": "#8B3DAF",
    "purple_08": "#7B349D",
    "purple_09": "#6F328A",
    "purple_10": "#642D7E",
    "purple_11": "#5B2871",
    "purple_12": "#4D2161",
    "purple_13": "#3F1A50",
    "purple_14": "#321441",
    "purple_15": "#260E32",

    "gray": "#6B7280",
}

PROPORTION_PALETTE = [
    COLOR_PALETTE["purple_01"],
    COLOR_PALETTE["purple_03"],
    COLOR_PALETTE["purple_05"],
    COLOR_PALETTE["purple_07"],
    COLOR_PALETTE["purple_09"],
    COLOR_PALETTE["purple_11"],
    COLOR_PALETTE["purple_13"],
    COLOR_PALETTE["purple_15"],
]

ORDINAL_PURPLE_RAMP = [
    COLOR_PALETTE["purple_01"],
    COLOR_PALETTE["purple_03"],
    COLOR_PALETTE["purple_05"],
    COLOR_PALETTE["purple_07"],
    COLOR_PALETTE["purple_09"],
    COLOR_PALETTE["purple_11"],
]

ORANGE_PEACH_CORE_RAMP = [
    COLOR_PALETTE["orange_dark_01"],
    COLOR_PALETTE["orange_dark_02"],
    COLOR_PALETTE["orange_base"],
    COLOR_PALETTE["peach_02"],
    COLOR_PALETTE["peach_04"],
    COLOR_PALETTE["peach_06"],
    COLOR_PALETTE["peach_08"],
    COLOR_PALETTE["peach_10"],
    COLOR_PALETTE["peach_12"],
]

PURPLE_ORANGE_EXTENDED_RAMP = [
    COLOR_PALETTE["purple_01"],
    COLOR_PALETTE["orange_dark_01"],
    COLOR_PALETTE["purple_03"],
    COLOR_PALETTE["orange_dark_02"],
    COLOR_PALETTE["purple_05"],
    COLOR_PALETTE["orange_base"],
    COLOR_PALETTE["purple_07"],
    COLOR_PALETTE["peach_02"],
    COLOR_PALETTE["purple_09"],
    COLOR_PALETTE["peach_04"],
    COLOR_PALETTE["purple_11"],
    COLOR_PALETTE["peach_06"],
    COLOR_PALETTE["purple_13"],
    COLOR_PALETTE["peach_08"],
    COLOR_PALETTE["purple_15"],
    COLOR_PALETTE["peach_10"],
    COLOR_PALETTE["purple_02"],
    COLOR_PALETTE["peach_12"],
    COLOR_PALETTE["purple_04"],
    COLOR_PALETTE["purple_06"],
    COLOR_PALETTE["purple_08"],
    COLOR_PALETTE["purple_10"],
    COLOR_PALETTE["purple_12"],
    COLOR_PALETTE["purple_14"],
]

TOPIC_PALETTES = {
    "clima_koppen": PURPLE_ORANGE_EXTENDED_RAMP,
    "edafologia": PURPLE_ORANGE_EXTENDED_RAMP,
    "geologia": PURPLE_ORANGE_EXTENDED_RAMP,
}

LIGHT_GRID = "#E5E7EB"
AXIS_COLOR = "#9CA3AF"
TEXT_COLOR = "#111827"
MONTH_ORDER = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
MONTH_LABELS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

EXPLICIT_COLOR_MAPS = {
    "acuiferos": {
        "con_disponibilidad": COLOR_PALETTE["purple_09"],
        "sin_disponibilidad": COLOR_PALETTE["purple_01"],
        "no_explotado": COLOR_PALETTE["purple_05"],
        "sobreexplotado": COLOR_PALETTE["orange"],
    },

    "sequia": {
        "sin_sequia": COLOR_PALETTE["purple_01"],
        "anormalmente_seco": COLOR_PALETTE["purple_03"],
        "sequia_moderada": COLOR_PALETTE["purple_05"],
        "sequia_severa": COLOR_PALETTE["purple_07"],
        "sequia_extrema": COLOR_PALETTE["purple_09"],
        "sequia_excepcional": COLOR_PALETTE["orange"],
    },

    "pendiente_clasificada": {
        "0_a_2": COLOR_PALETTE["purple_01"],
        "mayor_a_2_y_hasta_5": COLOR_PALETTE["purple_03"],
        "mayor_a_5_y_hasta_10": COLOR_PALETTE["purple_05"],
        "mayor_a_10_y_hasta_15": COLOR_PALETTE["purple_07"],
        "mayor_a_15_y_hasta_30": COLOR_PALETTE["purple_09"],
        "mayor_a_30": COLOR_PALETTE["orange"],
    },

    "ndvi": {
        "sin_vegetacion": COLOR_PALETTE["purple_01"],
        "sin_vegetacion_superficies_no_vegetadas": COLOR_PALETTE["purple_01"],
        "vegetacion_muy_escasa": COLOR_PALETTE["purple_03"],
        "vegetacion_escasa": COLOR_PALETTE["purple_05"],
        "vegetacion_moderada": COLOR_PALETTE["purple_07"],
        "vegetacion_densa": COLOR_PALETTE["orange"],
    },

    "ndwi": {
        "vegetacion_muy_seca": COLOR_PALETTE["purple_01"],
        "vegetacion_muy_seca_estres_hidrico_alto": COLOR_PALETTE["purple_01"],
        "vegetacion_seca": COLOR_PALETTE["purple_03"],
        "condicion_hidrica_baja": COLOR_PALETTE["purple_05"],
        "condicion_hidrica_moderada": COLOR_PALETTE["purple_07"],
        "alta_humedad_en_vegetacion": COLOR_PALETTE["orange"],
    },

    "erosion_potencial": {
        "erosion_muy_baja": COLOR_PALETTE["purple_01"],
        "erosion_baja": COLOR_PALETTE["purple_03"],
        "erosion_leve": COLOR_PALETTE["purple_05"],
        "erosion_moderada": COLOR_PALETTE["purple_07"],
        "erosion_grave": COLOR_PALETTE["purple_09"],
        "erosion_muy_grave": COLOR_PALETTE["purple_11"],
        "erosion_extrema": COLOR_PALETTE["orange"],
    },

    "erosion_efectiva": {
        "erosion_muy_baja": COLOR_PALETTE["purple_01"],
        "erosion_baja": COLOR_PALETTE["purple_03"],
        "erosion_leve": COLOR_PALETTE["purple_05"],
        "erosion_moderada": COLOR_PALETTE["purple_07"],
        "erosion_grave": COLOR_PALETTE["purple_09"],
        "erosion_muy_grave": COLOR_PALETTE["purple_11"],
        "erosion_extrema": COLOR_PALETTE["orange"],
    },
}


@dataclass
class TopicResult:
    topic: str
    status: str
    generated: int = 0
    output_dir: str = ""
    message: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SimpleTopic:
    key: str
    source: str
    title: str
    prefix: str
    value_col: str = "porcentaje"
    category_col: str = "categoria"
    sort_col: str | None = "orden_pct"
    max_categories: int = 12
    min_label_pct: float = 0.0


SIMPLE_TOPICS = [
    SimpleTopic("uso_suelo", "uso_suelo/uso_suelo_estadistica_detalle.csv", "Uso de suelo y vegetacion", "usv"),
    SimpleTopic("clima_koppen", "clima_koppen/clima_koppen_estadistica_detalle.csv", "Clima Koppen", "clima"),
    SimpleTopic("sequia", "sequia/sequia_estadistica_detalle.csv", "Sequia", "sequia", sort_col="orden_clase"),
    SimpleTopic(
        "pendiente_clasificada",
        "pendiente_clasificada/pendiente_clasificada_estadistica_detalle.csv",
        "Pendiente clasificada",
        "pendiente",
        sort_col="orden_clase",
    ),
    SimpleTopic("itur_index_cat", "itur_index_cat/itur_index_cat_estadistica_detalle.csv", "Indice ITUR", "itur"),
    SimpleTopic("ndwi", "ndwi/ndwi_estadistica_detalle.csv", "NDWI", "ndwi", sort_col="orden_clase"),
    SimpleTopic("edafologia", "edafologia/edafologia_estadistica_detalle.csv", "Edafologia", "edafologia"),
    SimpleTopic(
        "erosion_potencial",
        "erosion_potencial/erosion_potencial_estadistica_detalle.csv",
        "Erosion potencial",
        "erosion_pot",
        sort_col="orden_clase",
    ),
    SimpleTopic(
        "erosion_efectiva",
        "erosion_efectiva/erosion_efectiva_estadistica_detalle.csv",
        "Erosion efectiva",
        "erosion_efec",
        sort_col="orden_clase",
    ),
    SimpleTopic("ndvi", "ndvi/ndvi_estadistica_detalle.csv", "NDVI", "ndvi", sort_col="orden_clase"),
    SimpleTopic("geologia", "geologia/geologia_estadistica_detalle.csv", "Geologia", "geologia"),
]


def normalize_token(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def safe_slug(value: object) -> str:
    slug = normalize_token(value)
    return slug or "sin_nombre"


def setup_logging(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(output_root / "graficas_cuadernillos.log", mode="w", encoding="utf-8"),
        ],
    )


def setup_style() -> None:
    try:
        fm.findfont(FONT_FAMILY, fallback_to_default=False)
        plt.rcParams["font.family"] = FONT_FAMILY
    except ValueError:
        font_candidates = [
            Path.home() / ".local/share/fonts/Google Fonts/Lexend/Lexend_Regular.26.ttf",
            Path.home() / ".local/share/fonts/Lexend/Lexend-Regular.ttf",
            Path("/usr/share/fonts/truetype/lexend/Lexend-Regular.ttf"),
        ]
        for font_path in font_candidates:
            if font_path.exists():
                fm.fontManager.addfont(str(font_path))
                plt.rcParams["font.family"] = FONT_FAMILY
                break
        else:
            plt.rcParams["font.family"] = FALLBACK_FONT
            logging.warning("No se encontro Lexend; se usara %s.", FALLBACK_FONT)

    plt.rcParams.update(
        {
            "axes.edgecolor": AXIS_COLOR,
            "axes.labelcolor": TEXT_COLOR,
            "xtick.color": TEXT_COLOR,
            "ytick.color": TEXT_COLOR,
            "text.color": TEXT_COLOR,
            "figure.dpi": 120,
            "savefig.dpi": DPI,
        }
    )


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el CSV: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [normalize_token(col) for col in df.columns]
    text_cols = [
        col
        for col in df.columns
        if pd.api.types.is_object_dtype(df[col].dtype) or pd.api.types.is_string_dtype(df[col].dtype)
    ]
    for col in text_cols:
        df[col] = df[col].map(clean_text)
    for col in df.columns:
        if col not in {"nombre", "categoria", "cadena_texto", "campo_origen", "acuiferos_txt", "cuencas_txt"}:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().any():
                df[col] = converted
    return df


def coerce_numeric(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def require_columns(df: pd.DataFrame, required: list[str], topic: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{topic}: faltan columnas requeridas: {', '.join(missing)}")


def summarize_categories(df: pd.DataFrame, category_col: str, value_col: str, sort_col: str | None) -> pd.DataFrame:
    work = df.copy()
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce").fillna(0)
    agg = {value_col: "sum"}
    if sort_col and sort_col in work.columns:
        agg[sort_col] = "min"
    if "superficie_ha_aj" in work.columns:
        agg["superficie_ha_aj"] = "sum"
    elif "superficie_ha" in work.columns:
        agg["superficie_ha"] = "sum"

    out = work.groupby(category_col, dropna=False, as_index=False).agg(agg)
    out[category_col] = out[category_col].map(clean_text)
    out = out[out[category_col] != ""]
    out = out[out[value_col] > 0]
    if sort_col and sort_col in out.columns:
        out = out.sort_values([sort_col, value_col], ascending=[True, False])
    else:
        out = out.sort_values(value_col, ascending=False)
    return out.reset_index(drop=True)


def collapse_small_categories(df: pd.DataFrame, category_col: str, value_col: str, max_categories: int) -> pd.DataFrame:
    if len(df) <= max_categories:
        return df
    keep = df.head(max_categories - 1).copy()
    other = df.iloc[max_categories - 1:].copy()
    row = {
        category_col: "Otros",
        value_col: other[value_col].sum(),
    }
    return pd.concat([keep, pd.DataFrame([row])], ignore_index=True)


def get_legend_layout(topic_key: str, n_categories: int) -> int:
    if n_categories <= 0:
        return 1
    if topic_key == "uso_suelo":
        if n_categories <= 5:
            return n_categories
        if n_categories == 6:
            return 3
        return 4
    if topic_key == "acuiferos":
        return min(4, n_categories)
    if topic_key == "cuencas":
        return min(6, n_categories)
    if topic_key == "itur_index_cat":
        return min(5, n_categories)
    if topic_key == "sequia":
        return 6 if n_categories <= 6 else 3
    if topic_key.startswith("erosion_"):
        return 4 if n_categories >= 7 else min(4, n_categories)
    if topic_key in {"edafologia", "geologia"}:
        if n_categories <= 5:
            return n_categories
        return max(1, math.ceil(n_categories / 2))
    if topic_key == "clima_koppen":
        return min(8 if n_categories <= 16 else 9, n_categories)
    return min(max(1, math.ceil(n_categories / 2)), 6)


def reorder_legend_rowwise(handles: list[Patch], labels: list[str], ncol: int) -> tuple[list[Patch], list[str]]:
    if ncol <= 1 or len(handles) <= 2:
        return handles, labels
    nrows = math.ceil(len(handles) / ncol)
    handle_grid = [handles[row * ncol : (row + 1) * ncol] for row in range(nrows)]
    label_grid = [labels[row * ncol : (row + 1) * ncol] for row in range(nrows)]
    ordered_handles: list[Patch] = []
    ordered_labels: list[str] = []
    for col in range(ncol):
        for row in range(nrows):
            if col < len(handle_grid[row]):
                ordered_handles.append(handle_grid[row][col])
                ordered_labels.append(label_grid[row][col])
    return ordered_handles, ordered_labels


def global_category_order(df: pd.DataFrame, category_col: str, sort_col: str | None) -> list[str]:
    work = df[[category_col] + ([sort_col] if sort_col and sort_col in df.columns else [])].copy()
    work[category_col] = work[category_col].map(clean_text)
    work = work[work[category_col] != ""]
    if sort_col and sort_col in work.columns:
        order = work.groupby(category_col, as_index=False)[sort_col].min().sort_values([sort_col, category_col])
        return order[category_col].tolist()
    return sorted(work[category_col].dropna().unique(), key=lambda value: normalize_token(value))


def build_color_lookup(topic_key: str, categories: list[str]) -> dict[str, str]:
    explicit = EXPLICIT_COLOR_MAPS.get(topic_key, {})
    palette = TOPIC_PALETTES.get(topic_key, PROPORTION_PALETTE)
    lookup: dict[str, str] = {}
    palette_idx = 0
    for category in categories:
        key = normalize_token(category)
        if key in explicit:
            lookup[key] = explicit[key]
        else:
            lookup[key] = palette[palette_idx % len(palette)]
            palette_idx += 1
    lookup.setdefault("otros", COLOR_PALETTE["gray"])
    return lookup


def color_for_category(category: object, color_lookup: dict[str, str]) -> str:
    key = normalize_token(category)
    return color_lookup.get(key, PROPORTION_PALETTE[0])


def contrast_text_color(hex_color: str) -> str:
    """Elige texto claro u oscuro segun luminancia del color de fondo."""
    color = hex_color.lstrip("#")
    if len(color) != 6:
        return "white"
    red, green, blue = (int(color[idx : idx + 2], 16) for idx in (0, 2, 4))
    luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255
    return TEXT_COLOR if luminance > 0.62 else "white"


def display_label(topic_key: str, category: object) -> str:
    key = normalize_token(category)
    label_overrides = {
        ("ndvi", "sin_vegetacion"): "Sin vegetación",
        ("ndvi", "sin_vegetacion_superficies_no_vegetadas"): "Sin vegetación",
        ("ndwi", "vegetacion_muy_seca"): "Vegetación muy seca",
        ("ndwi", "vegetacion_muy_seca_estres_hidrico_alto"): "Vegetación muy seca",
    }
    return label_overrides.get((topic_key, key), str(category))


def save_figure(fig: plt.Figure, path: Path, transparent: bool = TRANSPARENT_BG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.02, transparent=transparent)
    plt.close(fig)


def split_rectangles(values: list[float], x: float, y: float, width: float, height: float) -> list[tuple[float, float, float, float]]:
    if not values:
        return []
    total = sum(values)
    if total <= 0:
        return []
    if len(values) == 1:
        return [(x, y, width, height)]

    half = total / 2
    running = 0.0
    split_at = 0
    for idx, value in enumerate(values):
        if idx > 0 and running + value > half:
            break
        running += value
        split_at = idx + 1
    split_at = max(1, min(split_at, len(values) - 1))

    first_values = values[:split_at]
    second_values = values[split_at:]
    first_total = sum(first_values)
    ratio = first_total / total

    if width >= height:
        first_width = width * ratio
        return split_rectangles(first_values, x, y, first_width, height) + split_rectangles(
            second_values, x + first_width, y, width - first_width, height
        )

    first_height = height * ratio
    return split_rectangles(first_values, x, y, width, first_height) + split_rectangles(
        second_values, x, y + first_height, width, height - first_height
    )


def plot_proportional_blocks(
    data: pd.DataFrame,
    topic_key: str,
    output_path: Path,
    category_col: str,
    value_col: str,
    color_lookup: dict[str, str],
) -> None:
    plot_df = data.copy()
    plot_df[value_col] = pd.to_numeric(plot_df[value_col], errors="coerce").fillna(0)
    plot_df = plot_df[plot_df[value_col] > 0].reset_index(drop=True)
    if plot_df.empty:
        raise ValueError("No hay valores positivos para graficar.")

    categories = plot_df[category_col].astype(str).tolist()
    values = plot_df[value_col].astype(float).tolist()
    colors = {category: color_for_category(category, color_lookup) for category in categories}
    treemap_height = CHART_STYLE["treemap_height"]
    rects = split_rectangles(values, 0, 0, 100, treemap_height)

    fig, ax = plt.subplots(figsize=CHART_STYLE["figsize_proportion"])
    ax.set_xlim(0, 100)
    ax.set_ylim(-12, treemap_height + 2)
    ax.axis("off")

    for (x, y, width, height), category, value in zip(rects, categories, values):
        ax.add_patch(
            Rectangle(
                (x, y),
                width,
                height,
                facecolor=colors[category],
                edgecolor="none",
                linewidth=0,
            )
        )
        area_share = (width * height) / (100 * treemap_height)
        if (
            area_share >= CHART_STYLE["treemap_label_area_min"]
            and width >= CHART_STYLE["treemap_label_width_min"]
            and height >= CHART_STYLE["treemap_label_height_min"]
        ):
            ax.text(
                x + width / 2,
                y + height / 2,
                f"{value:.1f} %",
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold",
                color=contrast_text_color(colors[category]),
            )

    handles = [Patch(facecolor=colors[category], edgecolor="none", label=category) for category in categories]
    labels = [display_label(topic_key, category) for category in categories]
    ncol = get_legend_layout(topic_key, len(handles))
    handles, labels = reorder_legend_rowwise(handles, labels, ncol)
    legend_fontsize = 6.2 if len(handles) > 36 else 7.0 if len(handles) > 20 else 8.2
    ax.legend(
        handles=handles,
        labels=labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.005),
        ncol=ncol,
        frameon=False,
        fontsize=legend_fontsize,
        handlelength=1.0,
        columnspacing=0.9,
        labelspacing=0.8,
    )
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    save_figure(fig, output_path)


def generate_simple_topic(
    spec: SimpleTopic,
    results_root: Path,
    output_root: Path,
    max_municipios: int | None = None,
) -> TopicResult:
    source_path = results_root / spec.source
    output_dir = output_root / spec.key
    result = TopicResult(topic=spec.key, status="ok", output_dir=str(output_dir))
    df = read_table(source_path)

    if spec.category_col not in df.columns:
        candidates = ["categoria", "tipo", "nivel", "tecno_simp", "index_cat", "class_value"]
        found = next((col for col in candidates if col in df.columns), None)
        if not found:
            raise ValueError(f"{spec.key}: no hay columna de categoria reconocible.")
        df = df.rename(columns={found: spec.category_col})
        result.warnings.append(f"Columna de categoria inferida: {found}.")

    require_columns(df, ["nombre", spec.category_col, spec.value_col], spec.key)
    df[spec.value_col] = coerce_numeric(df, spec.value_col).fillna(0)
    categories = global_category_order(df, spec.category_col, spec.sort_col)
    color_lookup = build_color_lookup(spec.key, categories)

    municipios = sorted(df["nombre"].dropna().unique())
    if max_municipios:
        municipios = municipios[:max_municipios]

    for municipio in municipios:
        try:
            data = summarize_categories(df[df["nombre"] == municipio], spec.category_col, spec.value_col, spec.sort_col)
            data = collapse_small_categories(data, spec.category_col, spec.value_col, spec.max_categories)
            if data.empty:
                result.warnings.append(f"{municipio}: sin valores positivos.")
                continue
            filename = f"{spec.prefix}_{safe_slug(municipio)}.png"
            plot_proportional_blocks(
                data,
                spec.key,
                output_dir / filename,
                spec.category_col,
                spec.value_col,
                color_lookup,
            )
            result.generated += 1
        except Exception as exc:  # noqa: BLE001 - se registra y continua con el siguiente municipio
            result.warnings.append(f"{municipio}: {exc}")

    return result


def aggregate_for_stacked(df: pd.DataFrame, municipio: str) -> dict[str, float]:
    work = df[df["nombre"] == municipio].copy()
    if work.empty:
        return {}
    require_columns(work, ["categoria", "porcentaje"], "barras apiladas")
    work["porcentaje"] = coerce_numeric(work, "porcentaje").fillna(0)
    agg = {"porcentaje": "sum"}
    sort_col = "orden_clase" if "orden_clase" in work.columns else "orden_pct" if "orden_pct" in work.columns else None
    if sort_col:
        agg[sort_col] = "min"
    out = work.groupby("categoria", as_index=False).agg(agg)
    out = out[out["porcentaje"] > 0]
    if sort_col:
        out = out.sort_values([sort_col, "porcentaje"], ascending=[True, False])
    else:
        out = out.sort_values("porcentaje", ascending=False)
    return dict(zip(out["categoria"], out["porcentaje"]))


def plot_stacked_pair(
    rows: list[tuple[str, dict[str, float]]],
    topic_key: str,
    output_path: Path,
    color_lookup: dict[str, str],
) -> None:
    categories = []
    for _, values in rows:
        categories.extend([cat for cat, value in values.items() if value > 0])
    colors = {category: color_for_category(category, color_lookup) for category in dict.fromkeys(categories)}

    fig, ax = plt.subplots(figsize=CHART_STYLE["figsize_stacked"])
    ax.set_xlim(-22, 100)
    ax.set_ylim(-0.70, len(rows) - 0.25)
    ax.axis("off")

    for y, (row_label, values) in enumerate(rows):
        left = 0.0
        for cat, value in values.items():
            if value <= 0:
                continue
            ax.barh(y, value, left=left, color=colors[cat], edgecolor="none", linewidth=0, height=0.72, label=cat)
            if value >= 6:
                ax.text(
                    left + value / 2,
                    y,
                    f"{value:.1f} %",
                    ha="center",
                    va="center",
                    color=contrast_text_color(colors[cat]),
                    fontsize=9.5,
                    fontweight="bold",
                )
            left += value
        ax.text(-3.0, y, row_label, ha="right", va="center", fontsize=11, fontweight="bold")

    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    if unique:
        legend_labels = list(unique.keys())
        legend_handles = list(unique.values())
        ncol = get_legend_layout(topic_key, len(unique))
        legend_handles, legend_labels = reorder_legend_rowwise(legend_handles, legend_labels, ncol)
        ax.legend(
            legend_handles,
            legend_labels,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.04),
            ncol=ncol,
            frameon=False,
            fontsize=8.2,
            handlelength=1.0,
            columnspacing=0.9,
        )

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    save_figure(fig, output_path)


def generate_acuiferos(results_root: Path, output_root: Path, max_municipios: int | None = None) -> TopicResult:
    key = "acuiferos"
    output_dir = output_root / key
    result = TopicResult(topic=key, status="ok", output_dir=str(output_dir))
    situacion = read_table(results_root / "acuiferos_situacion" / "acuiferos_situacion_estadistica_detalle.csv")
    condicion = read_table(results_root / "acuiferos_condicion" / "acuiferos_condicion_estadistica_detalle.csv")
    for df, label in [(situacion, "acuiferos_situacion"), (condicion, "acuiferos_condicion")]:
        require_columns(df, ["nombre", "categoria", "porcentaje"], label)
    categories = global_category_order(pd.concat([situacion, condicion], ignore_index=True), "categoria", "orden_pct")
    color_lookup = build_color_lookup(key, categories)

    municipios = sorted(set(situacion["nombre"].unique()) | set(condicion["nombre"].unique()))
    if max_municipios:
        municipios = municipios[:max_municipios]

    for municipio in municipios:
        try:
            rows = [
                ("Condición", aggregate_for_stacked(condicion, municipio)),
                ("Situación", aggregate_for_stacked(situacion, municipio)),
            ]
            if not any(sum(values.values()) > 0 for _, values in rows):
                continue
            plot_stacked_pair(rows, key, output_dir / f"acuiferos_{safe_slug(municipio)}.png", color_lookup)
            result.generated += 1
        except Exception as exc:  # noqa: BLE001
            result.warnings.append(f"{municipio}: {exc}")
    return result


def generate_cuencas(results_root: Path, output_root: Path, max_municipios: int | None = None) -> TopicResult:
    key = "cuencas"
    output_dir = output_root / key
    result = TopicResult(topic=key, status="ok", output_dir=str(output_dir))
    disponibilidad = read_table(results_root / "cuencas_clasificac" / "cuencas_clasificac_estadistica_detalle.csv")
    ordenamiento = read_table(results_root / "cuencas_categ" / "cuencas_categ_estadistica_detalle.csv")
    for df, label in [(disponibilidad, "cuencas_clasificac"), (ordenamiento, "cuencas_categ")]:
        require_columns(df, ["nombre", "categoria", "porcentaje"], label)
    categories = global_category_order(pd.concat([disponibilidad, ordenamiento], ignore_index=True), "categoria", "orden_pct")
    color_lookup = build_color_lookup(key, categories)

    municipios = sorted(set(disponibilidad["nombre"].unique()) | set(ordenamiento["nombre"].unique()))
    if max_municipios:
        municipios = municipios[:max_municipios]

    for municipio in municipios:
        try:
            rows = [
                ("Ordenamiento", aggregate_for_stacked(ordenamiento, municipio)),
                ("Disponibilidad", aggregate_for_stacked(disponibilidad, municipio)),
            ]
            if not any(sum(values.values()) > 0 for _, values in rows):
                continue
            plot_stacked_pair(rows, key, output_dir / f"cuencas_{safe_slug(municipio)}.png", color_lookup)
            result.generated += 1
        except Exception as exc:  # noqa: BLE001
            result.warnings.append(f"{municipio}: {exc}")
    return result


def generate_vientos(results_root: Path, output_root: Path, max_municipios: int | None = None) -> TopicResult:
    key = "vientos_dominantes"
    output_dir = output_root / key
    result = TopicResult(topic=key, status="ok", output_dir=str(output_dir))
    path = WIND_CSV if results_root == RESULTS_ROOT else results_root / WIND_CSV.name
    df = read_table(path)
    grade_cols = sorted(
        [col for col in df.columns if re.fullmatch(r"grado_\d+", col)],
        key=lambda col: int(col.split("_")[1]),
    )
    if "cve_mun" in df.columns:
        id_col = "cve_mun"
    elif "municipio_clave" in df.columns:
        id_col = "municipio_clave"
    else:
        id_col = "nombre"
    require_columns(df, [id_col], key)
    if not grade_cols:
        raise ValueError("vientos_dominantes: no se encontraron columnas grado_*.")

    angles_deg = [int(col.split("_")[1]) for col in grade_cols]
    theta = np.deg2rad(angles_deg)
    width = np.deg2rad(26)
    rows = df.head(max_municipios) if max_municipios else df

    for _, row in rows.iterrows():
        try:
            if id_col in {"cve_mun", "municipio_clave"}:
                municipio_id = f"{int(float(row[id_col])):03d}"
            else:
                municipio_id = clean_text(row[id_col])
            values = pd.to_numeric(row[grade_cols], errors="coerce").fillna(0).to_numpy(dtype=float)
            if np.nansum(values) <= 0:
                result.warnings.append(f"{municipio_id}: sin frecuencias positivas.")
                continue
            max_val = float(np.nanmax(values))
            colors = ["#FF8300" if value == max_val else "#8F39B1" for value in values]

            fig = plt.figure(figsize=(5.2, 5.2))
            ax = fig.add_subplot(111, polar=True)
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)
            ax.bar(theta, values, width=width, bottom=0.0, color=colors, edgecolor="none", linewidth=0, alpha=0.95)
            ax.set_xticks(np.deg2rad([0, 90, 180, 270]))
            ax.set_xticklabels(["N", "E", "S", "O"], fontsize=11, fontweight="bold")
            radial_max = max(max_val * 1.12, 0.05)
            radial_ticks = np.linspace(radial_max / 4, radial_max, 4)
            ax.set_ylim(0, radial_max)
            ax.set_yticks(radial_ticks)
            ax.set_yticklabels([])
            ax.grid(True, axis="x", linestyle="--", alpha=0.30, color=AXIS_COLOR)
            ax.grid(True, axis="y", linestyle="-", alpha=0.22, color=AXIS_COLOR)
            ax.spines["polar"].set_color(AXIS_COLOR)

            for angle, value in zip(theta, values):
                if value < 0.05:
                    continue
                fontsize = min(8, max(4.5, 4 + (value / max_val) * 4))
                ax.text(
                    angle,
                    value * 0.78,
                    f"{value * 100:.0f} %",
                    ha="center",
                    va="center",
                    fontsize=fontsize,
                    fontweight="bold",
                    color="white",
                )

            save_figure(fig, output_dir / f"vientos_{safe_slug(municipio_id)}.png", transparent=False)
            result.generated += 1
        except Exception as exc:  # noqa: BLE001
            result.warnings.append(f"{row.get(id_col, 'sin_id')}: {exc}")
    return result


def monthly_rows(df: pd.DataFrame, municipio: str) -> pd.DataFrame:
    work = df[df["municipio"] == municipio].copy()
    work["periodo"] = work["periodo"].astype(str).str.upper().str.strip()
    work = work[work["periodo"].isin(MONTH_ORDER)].copy()
    work["periodo"] = pd.Categorical(work["periodo"], categories=MONTH_ORDER, ordered=True)
    return work.sort_values("periodo").reset_index(drop=True)


def plot_temperatura_mensual(data: pd.DataFrame, output_path: Path) -> None:
    x = np.arange(len(data))
    mean = pd.to_numeric(data["mean"], errors="coerce")
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    if {"min", "max"}.issubset(data.columns):
        min_values = pd.to_numeric(data["min"], errors="coerce")
        max_values = pd.to_numeric(data["max"], errors="coerce")
        ax.fill_between(x, min_values, max_values, color="#D8B5E8", alpha=0.28, linewidth=0)
    ax.plot(x, mean, color="#FF8300", linewidth=2.6, marker="o", markersize=5.5, markeredgewidth=0)
    for xpos, value in zip(x, mean):
        if pd.notna(value):
            ax.text(xpos, value + 0.35, f"{value:.1f}", ha="center", va="bottom", fontsize=8.5, color=TEXT_COLOR)
    ax.set_ylabel("°C", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(MONTH_LABELS, fontsize=9)
    ax.yaxis.grid(True, color=LIGHT_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.93, bottom=0.13)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    save_figure(fig, output_path)


def plot_precipitacion_mensual(data: pd.DataFrame, output_path: Path) -> None:
    x = np.arange(len(data))
    min_values = pd.to_numeric(data["min"], errors="coerce")
    max_values = pd.to_numeric(data["max"], errors="coerce")
    mean = pd.to_numeric(data["mean"], errors="coerce")
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    width = 0.23
    ax.bar(x - width, min_values, color="#8F39B1", edgecolor="none", width=width, label="Minimo")
    ax.bar(x, mean, color="#FF8300", edgecolor="none", width=width, label="Media")
    ax.bar(x + width, max_values, color="#622484", edgecolor="none", width=width, label="Maximo")
    ax.set_ylabel("mm", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(MONTH_LABELS, fontsize=9)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=3, frameon=False, fontsize=8.5)
    ax.yaxis.grid(True, color=LIGHT_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(AXIS_COLOR)
    ax.spines["bottom"].set_color(AXIS_COLOR)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.94, bottom=0.18)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    save_figure(fig, output_path)


def generate_monthly_climate(
    key: str,
    source: str,
    output_root: Path,
    results_root: Path,
    plotter: Callable[[pd.DataFrame, Path], None],
    prefix: str,
    max_municipios: int | None = None,
) -> TopicResult:
    output_dir = output_root / key
    result = TopicResult(topic=key, status="ok", output_dir=str(output_dir))
    source_path = results_root / source
    logging.info("%s: usando %s", key, source_path)
    df = read_table(source_path)
    require_columns(df, ["municipio", "periodo", "mean"], key)

    municipios = sorted(df["municipio"].dropna().unique())
    if max_municipios:
        municipios = municipios[:max_municipios]

    for municipio in municipios:
        try:
            data = monthly_rows(df, municipio)
            if len(data) < 12:
                result.warnings.append(f"{municipio}: faltan meses para serie mensual.")
                continue
            plotter(data, output_dir / f"{prefix}_{safe_slug(municipio)}.png")
            result.generated += 1
        except Exception as exc:  # noqa: BLE001
            result.warnings.append(f"{municipio}: {exc}")
    return result


def generate_temperatura(results_root: Path, output_root: Path, max_municipios: int | None = None) -> TopicResult:
    return generate_monthly_climate(
        "temperatura_hist",
        "temperatura_hist/temperatura_hist_long.csv",
        output_root,
        results_root,
        plot_temperatura_mensual,
        "temperatura",
        max_municipios,
    )


def generate_precipitacion(results_root: Path, output_root: Path, max_municipios: int | None = None) -> TopicResult:
    return generate_monthly_climate(
        "precipitacion_hist",
        "precipitacion_hist/precipitacion_hist_long.csv",
        output_root,
        results_root,
        plot_precipitacion_mensual,
        "precipitacion",
        max_municipios,
    )


def expected_omissions(results_root: Path) -> list[TopicResult]:
    omitted: list[TopicResult] = []
    seen: set[str] = set()
    for path in sorted(results_root.rglob("*_estadistica_detalle.csv")):
        rel_parts = path.relative_to(results_root).parts
        first = rel_parts[0]
        if first in EXCLUDED_TOPICS and first not in seen:
            omitted.append(TopicResult(topic=first, status="omitido", message=EXCLUDED_TOPICS[first]))
            seen.add(first)
    return omitted


def write_summary(results: list[TopicResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tema", "estatus", "graficas", "salida", "mensaje", "advertencias"])
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "tema": result.topic,
                    "estatus": result.status,
                    "graficas": result.generated,
                    "salida": result.output_dir,
                    "mensaje": result.message,
                    "advertencias": " | ".join(result.warnings[:20]),
                }
            )


def build_registry() -> dict[str, Callable[[Path, Path, int | None], TopicResult]]:
    registry: dict[str, Callable[[Path, Path, int | None], TopicResult]] = {
        "acuiferos": generate_acuiferos,
        "cuencas": generate_cuencas,
        "vientos_dominantes": generate_vientos,
        "temperatura_hist": generate_temperatura,
        "precipitacion_hist": generate_precipitacion,
    }

    for spec in SIMPLE_TOPICS:
        registry[spec.key] = lambda results_root, output_root, max_municipios, spec=spec: generate_simple_topic(
            spec, results_root, output_root, max_municipios
        )
    return registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera graficas de Cuadernillos Municipales IIEG 2026.")
    parser.add_argument("--results-root", type=Path, default=RESULTS_ROOT, help="Carpeta centralizada de resultados.")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT, help="Carpeta centralizada de graficas.")
    parser.add_argument("--tema", action="append", help="Tema especifico a generar. Puede repetirse.")
    parser.add_argument("--max-municipios", type=int, help="Limite opcional para pruebas.")
    parser.add_argument("--sin-vientos", action="store_true", help="No generar vientos dominantes.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.output_root)
    setup_style()

    registry = build_registry()
    requested = args.tema or list(registry.keys())
    if args.sin_vientos and "vientos_dominantes" in requested:
        requested = [topic for topic in requested if topic != "vientos_dominantes"]

    results: list[TopicResult] = []
    results.extend(expected_omissions(args.results_root))

    logging.info("Entrada: %s", args.results_root)
    logging.info("Salida: %s", args.output_root)

    for topic in requested:
        if topic not in registry:
            result = TopicResult(topic=topic, status="error", message="Tema no registrado.")
            results.append(result)
            logging.error("%s: tema no registrado.", topic)
            continue
        try:
            logging.info("Generando %s...", topic)
            result = registry[topic](args.results_root, args.output_root, args.max_municipios)
            result.status = "ok" if result.generated > 0 else "sin_salida"
            if result.warnings:
                logging.warning("%s: %s advertencias.", topic, len(result.warnings))
            logging.info("%s: %s graficas.", topic, result.generated)
        except Exception as exc:  # noqa: BLE001 - se aisla el error por tema
            result = TopicResult(topic=topic, status="error", message=str(exc))
            logging.exception("%s fallo: %s", topic, exc)
        results.append(result)

    write_summary(results, args.output_root / LOG_PATH.name)

    ok_count = sum(1 for result in results if result.status == "ok")
    generated = sum(result.generated for result in results)
    omitted = sum(1 for result in results if result.status == "omitido")
    errors = [result for result in results if result.status == "error"]

    print("\nResumen final")
    print(f"- Temas generados correctamente: {ok_count}")
    print(f"- Graficas generadas: {generated}")
    print(f"- Temas omitidos: {omitted}")
    print(f"- Temas con error: {len(errors)}")
    print(f"- Log/resumen: {args.output_root / LOG_PATH.name}")
    if errors:
        print("\nErrores:")
        for result in errors:
            print(f"- {result.topic}: {result.message}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
