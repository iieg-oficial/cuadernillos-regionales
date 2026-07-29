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
        prefix = "Asimismo," if has_anp else ""
        parts.append(
            f"{prefix} los humedales abarcan {pct_h} \\% del territorio municipal."
        )
    elif not has_anp:
        parts = [
            "El municipio no registra áreas naturales protegidas ni humedales "
            "dentro de su territorio."
        ]

    return " ".join(parts).rstrip(".")


SENTINELS = {"sin_dato", "sin dato", "nd", "n/d", "na", "n/a", "null", "none"}


def is_sentinel(value):
    text = str(value or "").replace("\\", "").strip()
    return not text or text.lower() in SENTINELS or text == ND


def join_names(names):
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return f"{', '.join(names[:-1])} y {names[-1]}"


def split_names(value):
    items = []
    current = []
    depth = 0
    for char in str(value or ""):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            items.append("".join(current))
            current = []
            continue
        current.append(char)
    items.append("".join(current))

    return [item for item in (raw.strip() for raw in items) if not is_sentinel(item)]


def build_energia_text(dominante, valor, pct, secundarios):
    tipo = str(dominante or "").strip()
    if is_sentinel(tipo):
        return (
            "No se dispone de información sobre unidades económicas "
            "relacionadas con energía para el municipio."
        )

    frase = (
        f"Con respecto a unidades económicas relacionadas con energías, "
        f"predomina el tipo de {tipo}, con un valor de {valor}, equivalente a "
        f"{pct} \\% del total identificado."
    )

    otros = [narrative_lower(nombre) for nombre in split_names(secundarios)]
    if not otros:
        return frase

    return (
        f"{frase} También se registran {join_names(otros)}, "
        f"que complementan la red energética municipal."
    )


def build_clima_text(
    predominante, pct_predominante, secundario, pct_secundario, otros_nombres, pct_otros
):
    tipo = str(predominante or "").strip()
    if is_sentinel(tipo):
        return (
            "No se dispone de información sobre los tipos de clima "
            "presentes en el municipio."
        )

    partes = [
        f"El municipio presenta un clima predominante de tipo {tipo}, "
        f"que abarca {pct_predominante} \\% del territorio."
    ]

    segundo = str(secundario or "").strip()
    if not is_sentinel(segundo):
        partes.append(
            f"En segundo lugar se presenta {segundo} con {pct_secundario} \\%."
        )

    otros = split_names(otros_nombres)
    if otros:
        partes.append(
            f"Además se identifican variantes como {join_names(otros)}, "
            f"que representan {pct_otros} \\%."
        )

    return " ".join(partes)


def build_acuiferos_text(nombres, pct_con, pct_sin):
    items = split_names(nombres)
    if not items:
        return (
            "No se dispone de información sobre los acuíferos "
            "que abarcan el territorio municipal."
        )

    if len(items) == 1:
        ubicacion = f"El territorio está ubicado dentro del acuífero {items[0]}."
    else:
        ubicacion = (
            f"El territorio está ubicado dentro de los acuíferos: {join_names(items)}."
        )

    con = to_number(strip_percent_symbol(pct_con))
    sin = to_number(strip_percent_symbol(pct_sin))

    if con is None or sin is None:
        return ubicacion

    if con <= 0:
        disponibilidad = (
            "La totalidad de la superficie municipal comprendida en ellos "
            "no cuenta con disponibilidad de agua subterránea."
        )
    elif sin <= 0:
        disponibilidad = (
            "La totalidad de la superficie municipal comprendida en ellos "
            "cuenta con disponibilidad de agua subterránea."
        )
    else:
        disponibilidad = (
            f"Del total de la superficie municipal comprendida en ellos, "
            f"{fmt(sin)} \\% no tiene disponibilidad y {fmt(con)} \\% "
            f"cuenta con disponibilidad de agua subterránea."
        )

    if len(items) == 1:
        disponibilidad = disponibilidad.replace("en ellos", "en él")

    return f"{ubicacion} {disponibilidad}"


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
