import math

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

from core.constants import COLOR_TEXTO
from core.utils.charts import setup_chart_style
from pipelines.geografia.charts.palettes import (
    has_topic_palette,
    normalize_category_key,
    normalize_token,
    resolve_topic_color,
)

DPI = 300

COLOR_PALETTE = {
    "orange": "#FF8300",
    "orange_base": "#FA8524",
    "orange_dark_01": "#8F3A0B",
    "orange_dark_02": "#B95712",
    "peach_02": "#FFA35C",
    "peach_04": "#FFB678",
    "peach_06": "#FFC894",
    "peach_08": "#FFD8AE",
    "peach_10": "#FFE4C6",
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

AXIS_COLOR = "#9CA3AF"
TEXT_COLOR = COLOR_TEXTO
FIGSIZE_PROPORTION = (10.4, 3.75)
TREEMAP_HEIGHT = 46
TREEMAP_LABEL_MIN_FONT_SIZE = 5.0
TREEMAP_LABEL_MAX_FONT_SIZE = 15.0
TREEMAP_LABEL_INNER_MARGIN = 0.82


def _contrast_text_color(hex_color):
    color = hex_color.lstrip("#")
    if len(color) != 6:
        return "white"
    r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return TEXT_COLOR if luminance > 0.62 else "white"


def _build_color_lookup(topic_key, categories):
    explicit = EXPLICIT_COLOR_MAPS.get(topic_key, {})
    has_palette = has_topic_palette(topic_key)
    palette = TOPIC_PALETTES.get(topic_key, PROPORTION_PALETTE)
    lookup = {}
    palette_idx = 0
    for cat in categories:
        key = normalize_category_key(topic_key, cat)
        if not has_palette and key in explicit:
            lookup[key] = explicit[key]
        elif not has_palette:
            lookup[key] = palette[palette_idx % len(palette)]
            palette_idx += 1
        else:
            fallback = explicit.get(key, palette[palette_idx % len(palette)])
            lookup[key] = resolve_topic_color(topic_key, cat, fallback)
            palette_idx += 1
    lookup.setdefault("otros", COLOR_PALETTE["gray"])
    return lookup


def _color_for(cat, lookup, topic_key=None):
    key = normalize_category_key(topic_key, cat) if topic_key else normalize_token(cat)
    return lookup.get(key, PROPORTION_PALETTE[0])


def _split_rectangles(values, x, y, w, h):
    if not values:
        return []
    total = sum(values)
    if total <= 0:
        return []
    if len(values) == 1:
        return [(x, y, w, h)]

    half = total / 2
    running = 0.0
    split_at = 0
    for idx, val in enumerate(values):
        if idx > 0 and running + val > half:
            break
        running += val
        split_at = idx + 1
    split_at = max(1, min(split_at, len(values) - 1))

    first = values[:split_at]
    second = values[split_at:]
    ratio = sum(first) / total

    if w >= h:
        fw = w * ratio
        return _split_rectangles(first, x, y, fw, h) + _split_rectangles(
            second, x + fw, y, w - fw, h
        )
    fh = h * ratio
    return _split_rectangles(first, x, y, w, fh) + _split_rectangles(
        second, x, y + fh, w, h - fh
    )


def _get_legend_ncol(topic_key, n):
    if n <= 0:
        return 1
    if topic_key == "uso_suelo":
        return n if n <= 5 else 3 if n == 6 else 4
    if topic_key in {"edafologia", "geologia"}:
        return n if n <= 5 else max(1, math.ceil(n / 2))
    if topic_key == "clima_koppen":
        return min(8 if n <= 16 else 9, n)
    if topic_key.startswith("erosion_"):
        return 4 if n >= 7 else min(4, n)
    if topic_key == "acuiferos":
        return n
    return min(max(1, math.ceil(n / 2)), 6)


def _reorder_legend(handles, labels, ncol):
    if ncol <= 1 or len(handles) <= 2:
        return handles, labels
    nrows = math.ceil(len(handles) / ncol)
    hg = [handles[r * ncol : (r + 1) * ncol] for r in range(nrows)]
    lg = [labels[r * ncol : (r + 1) * ncol] for r in range(nrows)]
    oh, ol = [], []
    for c in range(ncol):
        for r in range(nrows):
            if c < len(hg[r]):
                oh.append(hg[r][c])
                ol.append(lg[r][c])
    return oh, ol


def _setup_style():
    setup_chart_style(**{"figure.dpi": 120})


def _autofit_label(ax, renderer, text, w, h):
    x0, y0 = ax.transData.transform((0, 0))
    x1, y1 = ax.transData.transform((w, h))
    rect_w = abs(x1 - x0) * TREEMAP_LABEL_INNER_MARGIN
    rect_h = abs(y1 - y0) * TREEMAP_LABEL_INNER_MARGIN
    if rect_w <= 0 or rect_h <= 0:
        text.set_fontsize(TREEMAP_LABEL_MIN_FONT_SIZE)
        return
    size = rect_h / ax.get_figure().dpi * 72
    text.set_fontsize(size)
    bbox = text.get_window_extent(renderer)
    if bbox.width > 0:
        size = min(size, size * rect_w / bbox.width)
    size = min(TREEMAP_LABEL_MAX_FONT_SIZE, max(TREEMAP_LABEL_MIN_FONT_SIZE, size))
    text.set_fontsize(size)


def _save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.02, transparent=True)
    plt.close(fig)


def plot_proportional_blocks(categories, values, topic_key, output_path):
    _setup_style()
    colors = _build_color_lookup(topic_key, categories)
    rects = _split_rectangles(values, 0, 0, 100, TREEMAP_HEIGHT)

    fig, ax = plt.subplots(figsize=FIGSIZE_PROPORTION)
    ax.set_xlim(0, 100)
    ax.set_ylim(-12, TREEMAP_HEIGHT + 2)
    ax.axis("off")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    for (x, y, w, h), cat, val in zip(rects, categories, values):
        c = _color_for(cat, colors, topic_key)
        rect = Rectangle((x, y), w, h, facecolor=c, edgecolor="none", linewidth=0)
        ax.add_patch(rect)
        if val <= 0.2:
            continue
        label = f"{val:.1f} %"
        text = ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va="center",
            fontweight="bold",
            color=_contrast_text_color(c),
            clip_on=True,
        )
        _autofit_label(ax, renderer, text, w, h)
        text.set_clip_path(rect)

    handles = [
        Patch(facecolor=_color_for(c, colors, topic_key), edgecolor="none", label=c)
        for c in categories
    ]
    labels = list(categories)
    ncol = _get_legend_ncol(topic_key, len(handles))
    handles, labels = _reorder_legend(handles, labels, ncol)
    fontsize = 6.2 if len(handles) > 36 else 7.0 if len(handles) > 20 else 8.2
    ax.legend(
        handles=handles,
        labels=labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.005),
        ncol=ncol,
        frameon=False,
        fontsize=fontsize,
        handlelength=1.0,
        columnspacing=0.9,
        labelspacing=0.8,
    )
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    _save(fig, output_path)


def plot_stacked_pair(row_data, topic_key, output_path):
    _setup_style()
    all_cats = []
    for _, vals in row_data:
        all_cats.extend([c for c, v in vals.items() if v > 0])
    colors = _build_color_lookup(topic_key, list(dict.fromkeys(all_cats)))

    fig, ax = plt.subplots(figsize=(10.4, 2.85))
    ax.set_xlim(-22, 100)
    ax.set_ylim(-0.70, len(row_data) - 0.25)
    ax.axis("off")

    for y, (label, vals) in enumerate(row_data):
        left = 0.0
        for cat, val in vals.items():
            if val <= 0:
                continue
            c = _color_for(cat, colors, topic_key)
            ax.barh(
                y,
                val,
                left=left,
                color=c,
                edgecolor="none",
                linewidth=0,
                height=0.72,
                label=cat,
            )
            if val >= 6:
                ax.text(
                    left + val / 2,
                    y,
                    f"{val:.1f} %",
                    ha="center",
                    va="center",
                    color=_contrast_text_color(c),
                    fontsize=9.5,
                    fontweight="bold",
                )
            left += val
        ax.text(-3.0, y, label, ha="right", va="center", fontsize=11, fontweight="bold")

    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    if unique:
        ncol = _get_legend_ncol(topic_key, len(unique))
        lh, ll = _reorder_legend(list(unique.values()), list(unique.keys()), ncol)
        ax.legend(
            lh,
            ll,
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
    _save(fig, output_path)
