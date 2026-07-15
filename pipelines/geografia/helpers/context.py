from core.constants import ND
from pipelines.geografia.helpers.formatting import (
    first_value,
    fmt,
    fmt_int,
    is_positive,
    narrative_lower,
    strip_percent_symbol,
    to_number,
)

MONTHS = {
    "ENE": ("ene", "Enero"),
    "FEB": ("feb", "Febrero"),
    "MAR": ("mar", "Marzo"),
    "ABR": ("abr", "Abril"),
    "MAY": ("may", "Mayo"),
    "JUN": ("jun", "Junio"),
    "JUL": ("jul", "Julio"),
    "AGO": ("ago", "Agosto"),
    "SEP": ("sep", "Septiembre"),
    "OCT": ("oct", "Octubre"),
    "NOV": ("nov", "Noviembre"),
    "DIC": ("dic", "Diciembre"),
    "ANUAL": ("anual", "Anual"),
}


def climate_context(long_rows, prefix):
    out = {}
    for row in long_rows:
        periodo = str(row.get("periodo", "")).upper().strip()
        entry = MONTHS.get(periodo)
        if not entry:
            continue
        short, _ = entry
        out[f"{prefix}_min_{short}"] = fmt(row.get("min"))
        out[f"{prefix}_max_{short}"] = fmt(row.get("max"))
        out[f"{prefix}_med_{short}"] = fmt(row.get("mean"))
        if prefix == "pp":
            out[f"{prefix}_media_{short}"] = fmt(row.get("mean"))
    return out


def build_anp_text(ctx):
    municipio = first_value(ctx, "anp_nombre", "dg_nombre", "municipio") or ND
    has_anp = is_positive(ctx.get("anp_num_anp")) or is_positive(
        ctx.get("anp_superficie_anp")
    )
    has_humedales = is_positive(ctx.get("anp_pct_humedales"))

    if has_anp:
        count = ctx.get("anp_num_anp", ND)
        superficie = ctx.get("anp_superficie_anp", ND)
        pct_raw = ctx.get("anp_pct_anp", ND)
        pct = strip_percent_symbol(pct_raw) if pct_raw != ND else ND
        area_word = (
            "área natural protegida"
            if to_number(ctx.get("anp_num_anp")) == 1
            else "áreas naturales protegidas"
        )
        parts = [
            f"El municipio de {municipio} registra {count} {area_word}, "
            f"con una superficie de {superficie} hectáreas, equivalente a "
            f"{pct} \\% del territorio municipal."
        ]
    else:
        parts = [
            "El municipio no registra áreas naturales protegidas "
            "dentro de su territorio."
        ]

    if has_humedales:
        pct_h_raw = ctx.get("anp_pct_humedales", ND)
        pct_h = strip_percent_symbol(pct_h_raw) if pct_h_raw != ND else ND
        prefix = "Asimismo, " if has_anp else ""
        parts.append(
            f"{prefix}Los humedales abarcan {pct_h} \\% del territorio municipal."
        )
    elif not has_anp:
        parts = [
            "El municipio no registra áreas naturales protegidas ni humedales "
            "dentro de su territorio."
        ]

    return " ".join(parts).rstrip(".")


def build_linea_transmision_text(value):
    number = to_number(value)
    if number is None:
        return (
            "No se dispone de información sobre la longitud de redes "
            "de alta tensión para el municipio."
        )
    if number <= 0:
        return "No existen redes de alta tensión registradas."
    return f"Existen {fmt(number)} kilómetros lineales de redes de alta tensión."


def build_espacios_publicos_text(total, rows):
    number = to_number(total)
    if number == 1:
        opening = "En el municipio se registra 1 espacio público."
    else:
        opening = f"En el municipio se registran {fmt_int(number)} espacios públicos."

    ranked = []
    for row in rows or []:
        categoria = first_value(row, "categoria", default=None)
        porcentaje = first_value(row, "porcentaje", default=None)
        if categoria is None or not is_positive(porcentaje):
            continue
        ranked.append(
            (
                float(row.get("orden_pct", len(ranked) + 1) or len(ranked) + 1),
                narrative_lower(categoria),
                fmt(to_number(strip_percent_symbol(porcentaje))),
            )
        )

    ranked.sort(key=lambda item: item[0])
    if not ranked:
        return opening

    if len(ranked) == 1:
        detalle = (
            f"Predomina el tipo {ranked[0][1]}, que representa "
            f"{ranked[0][2]} \\% del total."
        )
    elif len(ranked) == 2:
        detalle = (
            f"Predomina el tipo {ranked[0][1]}, con {ranked[0][2]} \\% del total, "
            f"seguido de {ranked[1][1]}, con {ranked[1][2]} \\%."
        )
    else:
        detalle = (
            f"Predomina el tipo {ranked[0][1]}, con {ranked[0][2]} \\% del total, "
            f"seguido de {ranked[1][1]}, con {ranked[1][2]} \\%, y "
            f"{ranked[2][1]}, con {ranked[2][2]} \\%."
        )
        if len(ranked) > 3:
            detalle += " El resto de tipos concentra la proporción restante."

    return f"{opening} {detalle}"


def build_subestaciones_text(value):
    number = to_number(value)
    if number is None:
        return (
            "No se dispone de un conteo específico de subestaciones eléctricas "
            "para el municipio en los insumos actuales."
        )
    if number <= 0:
        return "No se registran subestaciones eléctricas en el municipio."
    if number == 1:
        return "El municipio cuenta con 1 subestación eléctrica."
    return f"El municipio cuenta con {fmt_int(value)} subestaciones eléctricas."


def municipal_value(rows, column):
    if not rows:
        return None
    row = rows[0] if isinstance(rows, list) else rows
    return row.get(column)
