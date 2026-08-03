ND = "\\ND"


def _plural(n, singular, plural):
    return singular if n == 1 else plural


def _texto_extremo(
    es_maximo, mes, total_meses_con_extremo, n_meses_analizados, total, fmt_int
):
    if total_meses_con_extremo == 1:
        etiqueta = (
            "más casos" if es_maximo else "la menor cantidad de carpetas abiertas"
        )
        verbo = "fue" if es_maximo else "es"
        verbo_accion = "abrieron" if es_maximo else "registraron"
        singular = "carpeta" if es_maximo else "caso"
        plural = "carpetas" if es_maximo else "casos"
        palabra = _plural(total, singular, plural)
        return (
            f"El mes con {etiqueta} {verbo} {mes}, cuando se "
            f"{verbo_accion} {fmt_int(total)} {palabra}."
        )

    calificativo = "mayor" if es_maximo else "menor"
    return (
        f"La {calificativo} cantidad de carpetas abiertas en un mes fue de "
        f"{fmt_int(total)}, registrada en {total_meses_con_extremo} de los "
        f"{n_meses_analizados} meses analizados."
    )


def build_carpetas_texto(
    total,
    mes_inicio,
    anio_inicio,
    mes_fin,
    anio_fin,
    total_primer_anio,
    total_segundo_anio,
    mes_mas_casos,
    total_mes_mas_casos,
    n_meses_max,
    mes_menos_casos,
    total_mes_menos_casos,
    n_meses_min,
    n_meses_analizados,
    promedio,
    fmt_int,
):
    periodo = f"de {mes_inicio} {anio_inicio} a {mes_fin} {anio_fin}"

    if total == 0:
        return (
            f"Durante el periodo {periodo}, no se registraron carpetas de "
            "investigación por delitos del fuero común en el municipio."
        )

    if total == 1:
        return (
            f"Durante el periodo {periodo}, se abrió 1 carpeta de "
            f"investigación, registrada en {mes_mas_casos}."
        )

    if total_mes_mas_casos == total_mes_menos_casos:
        return (
            f"Durante el periodo {periodo}, se abrieron un total de "
            f"{fmt_int(total)} carpetas de investigación, distribuidas de "
            "manera uniforme entre los meses analizados. El promedio de "
            "carpetas abiertas en los doce meses analizados en el municipio "
            f"es de {promedio}."
        )

    texto_max = _texto_extremo(
        True,
        mes_mas_casos,
        n_meses_max,
        n_meses_analizados,
        total_mes_mas_casos,
        fmt_int,
    )
    texto_min = _texto_extremo(
        False,
        mes_menos_casos,
        n_meses_min,
        n_meses_analizados,
        total_mes_menos_casos,
        fmt_int,
    )

    return (
        f"Durante el periodo {periodo}, se abrieron un total de "
        f"{fmt_int(total)} carpetas de investigación, de las cuales "
        f"{fmt_int(total_primer_anio)} se aperturaron en los meses de "
        f"{anio_inicio}, mientras que en los meses de {anio_fin} fueron "
        f"{fmt_int(total_segundo_anio)}. {texto_max} {texto_min} El promedio "
        "de carpetas abiertas en los doce meses analizados en el municipio "
        f"es de {promedio}."
    )


def build_bienes_juridicos_texto(municipio, periodo_texto, casos_bien_afectado, fmt):
    if not casos_bien_afectado:
        return (
            f"En {municipio}, {periodo_texto}, no se identificaron bienes "
            "jurídicos afectados por delitos del fuero común."
        )

    total_bienes = sum(r["total"] for r in casos_bien_afectado)
    nombres_pct = [
        (
            bien["bien_afectado"],
            fmt(bien["total"] / total_bienes * 100 if total_bienes else 0),
        )
        for bien in casos_bien_afectado
    ]

    if len(nombres_pct) == 1:
        nombre, pct = nombres_pct[0]
        return (
            f"En {municipio}, {periodo_texto}, el bien jurídico afectado con "
            f"mayor incidencia fue: {nombre} ({pct}\\,\\%)."
        )

    if len(nombres_pct) == 2:
        (n1, p1), (n2, p2) = nombres_pct
        return (
            f"En {municipio}, {periodo_texto}, los dos principales bienes "
            f"jurídicos afectados fueron: {n1} ({p1}\\,\\%) y {n2} ({p2}\\,\\%)."
        )

    (n1, p1), (n2, p2), (n3, p3) = nombres_pct[:3]
    return (
        f"En {municipio}, {periodo_texto}, los tres principales bienes "
        f"jurídicos afectados fueron: {n1} ({p1}\\,\\%), {n2} ({p2}\\,\\%), "
        f"{n3} ({p3}\\,\\%)."
    )


def build_delitos_texto(casos_por_delito, fmt_int):
    if not casos_por_delito:
        return (
            "No se identificaron subtipos de delitos con carpetas de "
            "investigación en el periodo analizado."
        )

    nombres_total = [(d["delito"], fmt_int(d["total"])) for d in casos_por_delito]

    if len(nombres_total) == 1:
        delito, total = nombres_total[0]
        return (
            "En el periodo de análisis en el municipio, el subtipo de "
            f"delito con más carpetas de investigación fue: {delito}, "
            f"con {total}."
        )

    if len(nombres_total) == 2:
        (d1, t1), (d2, t2) = nombres_total
        return (
            "En el periodo de análisis en el municipio, los dos subtipos "
            "de delitos con más carpetas de investigación fueron: "
            f"{d1}, con {t1}; y {d2}, con {t2}."
        )

    (d1, t1), (d2, t2), (d3, t3) = nombres_total[:3]
    return (
        "En el periodo de análisis en el municipio, los subtipos de "
        "delitos con más carpetas de investigación fueron: "
        f"{d1}, con {t1}; en segundo puesto se encuentra {d2}, con {t2}; "
        f"seguido de {d3}, con {t3}."
    )
