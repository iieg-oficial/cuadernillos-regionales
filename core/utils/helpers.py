import math

from core.constants import DASH, ND


def rows_have_na(rows):
    return any(value == DASH for row in rows for value in row.values())


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
