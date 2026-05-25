from pipelines.geografia.helpers.formatting import (
    first_value,
    fmt,
    is_positive,
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
        out[f"{prefix}_min_{short}"] = fmt(row.get("min"), field_name="min")
        out[f"{prefix}_max_{short}"] = fmt(row.get("max"), field_name="max")
        out[f"{prefix}_med_{short}"] = fmt(row.get("mean"), field_name="mean")
        if prefix == "pp":
            out[f"{prefix}_media_{short}"] = fmt(row.get("mean"), field_name="mean")
    return out


def build_anp_text(ctx):
    municipio = fmt(
        first_value(ctx, "anp_nombre", "dg_nombre", "municipio"),
        field_name="municipio",
    )
    has_anp = is_positive(ctx.get("anp_num_anp")) or is_positive(
        ctx.get("anp_superficie_anp")
    )
    has_humedales = is_positive(ctx.get("anp_pct_humedales"))

    if has_anp:
        count = fmt(ctx.get("anp_num_anp"), field_name="anp_num_anp")
        superficie = fmt(ctx.get("anp_superficie_anp"), field_name="anp_superficie_anp")
        pct = fmt(
            strip_percent_symbol(ctx.get("anp_pct_anp")), field_name="anp_pct_anp"
        )
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
        pct_h = fmt(
            strip_percent_symbol(ctx.get("anp_pct_humedales")),
            field_name="anp_pct_humedales",
        )
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
    return (
        f"Existen {fmt(value, field_name='longitud_km_total_municipio')} "
        "kilómetros lineales de redes de alta tensión."
    )


def municipal_value(rows, column):
    if not rows:
        return None
    row = rows[0] if isinstance(rows, list) else rows
    return row.get(column)
