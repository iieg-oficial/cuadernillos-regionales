import unicodedata

from pipelines.geografia.helpers.formatting import fmt, sentence_case, to_number


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
            current[out] = fmt(value, field_name=src)
        result.append(current)
    return result


def _sort_text_key(value):
    text = "" if value is None else str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


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
                "nombre_de_la_institucion": fmt(
                    row.get("nombre_de_la_institucion"),
                    field_name="nombre_de_la_institucion",
                ),
                "nivel_atencion": fmt(
                    health_level_label(row.get("nivel_de_atencion")),
                    field_name="nivel_de_atencion",
                ),
                "cantidad": fmt(row.get("conteo"), field_name="conteo"),
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

    work.sort(
        key=lambda r: (
            EDUCATION_LEVEL_ORDER.get(str(r.get("nivel", "")).strip(), 999),
            str(r.get("nivel", "")),
            EDUCATION_SECTOR_ORDER.get(
                str(r.get("sostenimiento_reclasificado", "")).strip(), 999
            ),
        )
    )

    result = []
    for row in work:
        nivel = str(row.get("nivel", "")).strip()
        nivel = EDUCATION_LEVEL_LABELS.get(nivel, nivel)
        result.append(
            {
                "nivel_educativo": fmt(nivel, field_name="nivel"),
                "sector": fmt(
                    row.get("sostenimiento_reclasificado"),
                    field_name="sostenimiento_reclasificado",
                ),
                "cantidad": fmt(row.get("conteo"), field_name="conteo"),
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
    return fmt(total, field_name=value_col) if total > 0 else "ND"


def sup_sum(rows, contains, value_col="superficie_ha"):
    return pct_sum(rows, contains, value_col)
