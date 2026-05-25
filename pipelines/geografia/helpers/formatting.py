import math
import re

ND = r"\ND"

DISPLAY_NUMBER_RE = re.compile(r"^\s*(-?\d+)(\.\d+)?\s*$")
RAW_FIELD_TOKENS = ("lat", "lon", "coord", "coordenada", "clave", "cve", "id")
RAW_FIELD_NAMES = {"class_value", "categoria"}
NUMERIC_FIELD_TOKENS = (
    "superficie",
    "porcentaje",
    "pct",
    "conteo",
    "total",
    "num",
    "cantidad",
    "min",
    "max",
    "mean",
    "med",
    "longitud",
    "area",
    "elevacion",
    "elev",
    "temp",
    "prec",
    "densidad",
)


def latex_escape(value):
    if value is None:
        return "ND"
    if isinstance(value, float) and math.isnan(value):
        return "ND"
    if isinstance(value, float):
        value = f"{value:.2f}".rstrip("0").rstrip(".")
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
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


def format_number_es(value):
    if value is None:
        return value
    if isinstance(value, float) and math.isnan(value):
        return value

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        text = str(value)
    elif isinstance(value, str):
        text = value.strip()
    else:
        return value

    match = DISPLAY_NUMBER_RE.match(text)
    if not match:
        return value

    try:
        from decimal import Decimal, InvalidOperation

        number = Decimal(match.group(1) + (match.group(2) or ""))
    except InvalidOperation:
        return value

    sign = "-" if number < 0 else ""
    plain = format(abs(number), "f")
    integer, dot, decimals = plain.partition(".")
    integer = f"{int(integer):,}".replace(",", r"\,")
    decimals = decimals.rstrip("0")
    return f"{sign}{integer}{dot}{decimals}" if decimals else f"{sign}{integer}"


def fmt(value, field_name=None):
    field = (field_name or "").lower()
    is_data_field = (
        field
        and field not in RAW_FIELD_NAMES
        and not any(token in field for token in RAW_FIELD_TOKENS)
    )
    is_numeric = is_data_field and any(t in field for t in NUMERIC_FIELD_TOKENS)
    if is_data_field:
        if is_numeric and (
            value is None or (isinstance(value, float) and math.isnan(value))
        ):
            return "0"
        formatted = format_number_es(value)
        if formatted is not value:
            return formatted
    return latex_escape(value)


def strip_percent_symbol(value):
    if value is None:
        return value
    if isinstance(value, float) and math.isnan(value):
        return value
    text = str(value).strip()
    return re.sub(r"\s*\\?%\s*$", "", text).strip()


def first_value(data, *keys, default="ND"):
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
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip().replace(",", "").replace("%", "")
    if not text or text.upper() == "ND":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def is_positive(value):
    number = to_number(value)
    return number is not None and number > 0


def sentence_case(value):
    if value is None:
        return value
    if isinstance(value, float) and math.isnan(value):
        return value
    text = str(value).strip()
    if not text:
        return text
    text = re.sub(r"\s+", " ", text.lower())
    return text[:1].upper() + text[1:]
