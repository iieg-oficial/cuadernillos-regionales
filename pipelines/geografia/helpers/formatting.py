import math
import re

from core.constants import ND


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


def latex_escape(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ND
    text = str(value)
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


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
