import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

from core.constants import COLOR_TEXTO
from core.utils.logger import Logger

FONT_FAMILY = "Lexend"
FALLBACK_FONT = "DejaVu Sans"
AXIS_COLOR = "#9CA3AF"
TEXT_COLOR = COLOR_TEXTO
DPI = 300

_font_checked = False
_resolved_font = None


def resolve_font():
    global _font_checked, _resolved_font
    if _font_checked:
        return _resolved_font

    _font_checked = True
    try:
        fm.findfont(FONT_FAMILY, fallback_to_default=False)
        _resolved_font = FONT_FAMILY
    except ValueError:
        Logger.warning(
            f"Fuente '{FONT_FAMILY}' no encontrada; "
            f"las graficas usaran '{FALLBACK_FONT}'. "
            f"Instala los TTF (ver README) y borra el cache de matplotlib."
        )
        _resolved_font = FALLBACK_FONT
    return _resolved_font


def setup_chart_style(**overrides):
    plt.rcParams["font.family"] = resolve_font()
    plt.rcParams.update(
        {
            "axes.edgecolor": AXIS_COLOR,
            "axes.labelcolor": TEXT_COLOR,
            "xtick.color": TEXT_COLOR,
            "ytick.color": TEXT_COLOR,
            "text.color": TEXT_COLOR,
            "savefig.dpi": DPI,
        }
    )
    if overrides:
        plt.rcParams.update(overrides)
