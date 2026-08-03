import math
import re

from core.constants import ND
from core.utils.helpers import latex_escape

__all__ = ["latex_escape"]


def fmt(value, decimals=2) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "0"
    return f"{round(value, decimals):,.{decimals}f}".replace(",", r"\,")


def fmt_int(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "0"
    return f"{int(value):,}".replace(",", r"\,")


def fmt_pct(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ND
    return f"{value:,.2f}".replace(",", r"\,") + r"\,\%"


def strip_percent_symbol(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return value
    text = str(value).strip()
    return re.sub(r"\s*\\?%\s*$", "", text).strip()


def first_value(data, *keys, default=None):
    for key in keys:
        value = data.get(key) if isinstance(data, dict) else getattr(data, key, None)
        if value is None:
            continue
        if isinstance(value, float) and math.isnan(value):
            continue
        text = str(value).strip()
        if text and text.upper() != "ND":
            return value
    return default


def to_number(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = str(value).strip().replace(r"\,", "").replace(",", "").replace("%", "")
    if not text or text.upper() == "ND" or text == r"\ND":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def is_positive(value):
    number = to_number(value)
    return number is not None and number > 0


def sentence_case(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return value
    text = str(value).strip()
    if not text:
        return text
    text = re.sub(r"\s+", " ", text.lower())
    return text[:1].upper() + text[1:]


COMPARATIVE_PLURALS = {"mayor": "mayores", "menor": "menores"}

COMPARATIVE_RE = re.compile(r"\b(mayor|menor) a\b")


def pluralize_comparatives(value):
    if value is None:
        return value
    text = str(value).strip()
    if not text or text.upper() == "ND":
        return value
    return COMPARATIVE_RE.sub(
        lambda match: f"{COMPARATIVE_PLURALS[match.group(1)]} a", text
    )


ABBREVIATION_RE = re.compile(r"\b[A-Z]\.(?:\s?[A-Z]\.)*")


def narrative_lower(value):
    if value is None:
        return value
    if isinstance(value, float) and math.isnan(value):
        return value
    text = str(value).strip()
    if not text or text.upper() == "ND":
        return text
    if text.isupper() and len(text) <= 8:
        return text
    if "(" in text and ")" in text and " " not in text:
        return text
    parts = []
    last_end = 0
    for match in ABBREVIATION_RE.finditer(text):
        parts.append(text[last_end : match.start()].lower())
        parts.append(match.group(0))
        last_end = match.end()
    parts.append(text[last_end:].lower())
    return "".join(parts)
