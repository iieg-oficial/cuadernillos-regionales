import unicodedata

from core.constants import ND
from pipelines.geografia.helpers.formatting import (
    fmt,
    fmt_int,
    latex_escape,
    sentence_case,
    to_number,
)
from pipelines.geografia.mappings import HEALTH_INSTITUTION_ACCENTS


def rows_for(rows, columns, order_col="orden_pct", transforms=None):
    work = list(rows)
    if order_col:
        work = sorted(
            work,
            key=lambda r: (
                float(r.get(order_col, 999)) if r.get(order_col) is not None else 999
            ),
        )
    transforms = transforms or {}
    result = []
    for row in work:
        current = {}
        for out, src in columns.items():
            value = row.get(src)
            transform = transforms.get(src)
            if transform is not None:
                value = transform(value)
            if value is None:
                current[out] = ND
            elif isinstance(value, float):
                current[out] = fmt(value)
            elif isinstance(value, int) and not isinstance(value, bool):
                current[out] = fmt_int(value)
            else:
                current[out] = latex_escape(value)
        result.append(current)
    return result


def _sort_text_key(value):
    text = "" if value is None else str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def health_institution_label(value):
    base = sentence_case(value)
    return HEALTH_INSTITUTION_ACCENTS.get(base, base)


def health_level_label(value):
    text = sentence_case(value)
    if _sort_text_key(text) == "no aplica":
        return "Otros"
    return text


def health_level_order(value):
    key = _sort_text_key(value)
    if "primer" in key:
        return 1
    if "segundo" in key:
        return 2
    if "tercer" in key:
        return 3
    if key == "no aplica":
        return 4
    return 999


def health_rows_for(rows):
    work = list(rows)
    if not work:
        return []

    work.sort(
        key=lambda r: (
            health_level_order(r.get("nivel_de_atencion")),
            _sort_text_key(r.get("nombre_de_la_institucion")),
        )
    )

    result = []
    for row in work:
        result.append(
            {
                "nombre_de_la_institucion": latex_escape(
                    health_institution_label(row.get("nombre_de_la_institucion"))
                ),
                "nivel_atencion": latex_escape(
                    health_level_label(row.get("nivel_de_atencion"))
                ),
                "cantidad": fmt_int(row.get("conteo")),
            }
        )
    return result


EDUCATION_LEVEL_ORDER = {
    "Inicial": 1,
    "Preescolar": 2,
    "Primaria": 3,
    "Secundaria": 4,
    "Bachillerato": 5,
    "Licenciatura": 6,
    "Profesional Tecnico": 7,
    "Técnico": 7,
}

EDUCATION_LEVEL_LABELS = {
    "Profesional Tecnico": "Técnico",
}

EDUCATION_SECTOR_ORDER = {"Público": 1, "Particular": 2}


def education_rows_for(rows):
    work = list(rows)
    if not work:
        return []

    niveles = {}
    for row in work:
        nivel = str(row.get("nivel", "")).strip()
        sector = str(row.get("sostenimiento_reclasificado", "")).strip()
        conteo = row.get("conteo") or 0
        bucket = niveles.setdefault(nivel, {"Público": 0, "Particular": 0})
        if sector in bucket:
            bucket[sector] += conteo

    ordered = sorted(
        niveles.items(),
        key=lambda item: (
            EDUCATION_LEVEL_ORDER.get(item[0], 999),
            item[0],
        ),
    )

    result = []
    for nivel, sectores in ordered:
        nivel = EDUCATION_LEVEL_LABELS.get(nivel, nivel)
        result.append(
            {
                "nivel_educativo": latex_escape(nivel),
                "publico": fmt_int(sectores["Público"]),
                "particular": fmt_int(sectores["Particular"]),
            }
        )
    return result


def pct_sum(rows, contains, value_col="porcentaje"):
    terms = [t.lower() for t in contains]
    total = 0.0
    for row in rows:
        cat = str(row.get("categoria", "")).lower()
        if any(t in cat for t in terms):
            val = to_number(row.get(value_col))
            if val is not None:
                total += val
    return fmt(total)


def sup_sum(rows, contains, value_col="superficie_ha"):
    return pct_sum(rows, contains, value_col)
