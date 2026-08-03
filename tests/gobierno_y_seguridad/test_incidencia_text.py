from pipelines.gobierno_y_seguridad.helpers.incidencia import (
    build_bienes_juridicos_texto,
    build_carpetas_texto,
    build_delitos_texto,
)


def _fmt_int(value) -> str:
    return f"{int(value):,}".replace(",", r"\,")


def _fmt(value, decimals=2) -> str:
    return f"{round(value, decimals):,.{decimals}f}".replace(",", r"\,")


def _texto_carpetas(
    total,
    mes_mas_casos="agosto de 2025",
    total_mes_mas_casos=1,
    n_meses_max=1,
    mes_menos_casos="julio de 2025",
    total_mes_menos_casos=0,
    n_meses_min=1,
    n_meses_analizados=12,
    promedio="0.08",
):
    return build_carpetas_texto(
        total=total,
        mes_inicio="julio",
        anio_inicio=2025,
        mes_fin="junio",
        anio_fin=2026,
        total_primer_anio=total,
        total_segundo_anio=0,
        mes_mas_casos=mes_mas_casos,
        total_mes_mas_casos=total_mes_mas_casos,
        n_meses_max=n_meses_max,
        mes_menos_casos=mes_menos_casos,
        total_mes_menos_casos=total_mes_menos_casos,
        n_meses_min=n_meses_min,
        n_meses_analizados=n_meses_analizados,
        promedio=promedio,
        fmt_int=_fmt_int,
    )


def test_zero_carpetas_states_none_were_opened():
    texto = _texto_carpetas(total=0, total_mes_mas_casos=0, total_mes_menos_casos=0)

    assert "no se registraron carpetas de investigación" in texto
    assert "El mes con más casos" not in texto
    assert "promedio" not in texto


def test_single_carpeta_uses_reduced_wording_without_min_max_or_average():
    texto = _texto_carpetas(total=1)

    assert "se abrió 1 carpeta de investigación" in texto
    assert "registrada en agosto de 2025" in texto
    assert "El mes con más casos" not in texto
    assert "promedio" not in texto


def test_uniform_distribution_skips_max_min_comparison():
    texto = _texto_carpetas(
        total=12,
        total_mes_mas_casos=1,
        total_mes_menos_casos=1,
        n_meses_max=12,
        n_meses_min=12,
    )

    assert "distribuidas de manera uniforme" in texto
    assert "El mes con más casos" not in texto
    assert "registrada en" not in texto


def test_unique_max_and_min_months_are_named():
    texto = _texto_carpetas(
        total=15,
        mes_mas_casos="agosto de 2025",
        total_mes_mas_casos=5,
        n_meses_max=1,
        mes_menos_casos="enero de 2026",
        total_mes_menos_casos=0,
        n_meses_min=1,
    )

    assert (
        "El mes con más casos fue agosto de 2025, cuando se abrieron 5 carpetas."
        in texto
    )
    assert (
        "El mes con la menor cantidad de carpetas abiertas es enero de 2026, "
        "cuando se registraron 0 casos." in texto
    )


def test_tied_minimum_months_are_summarized_without_listing_them():
    texto = _texto_carpetas(
        total=15,
        mes_mas_casos="agosto de 2025",
        total_mes_mas_casos=5,
        n_meses_max=1,
        mes_menos_casos="\\ND",
        total_mes_menos_casos=0,
        n_meses_min=8,
        n_meses_analizados=12,
    )

    assert (
        "La menor cantidad de carpetas abiertas en un mes fue de 0, "
        "registrada en 8 de los 12 meses analizados." in texto
    )
    assert "enero" not in texto
    assert "\\ND" not in texto


def test_tied_maximum_months_are_summarized_without_listing_them():
    texto = _texto_carpetas(
        total=15,
        mes_mas_casos="\\ND",
        total_mes_mas_casos=3,
        n_meses_max=3,
        mes_menos_casos="enero de 2026",
        total_mes_menos_casos=0,
        n_meses_min=1,
    )

    assert (
        "La mayor cantidad de carpetas abiertas en un mes fue de 3, "
        "registrada en 3 de los 12 meses analizados." in texto
    )
    assert "\\ND" not in texto


def test_no_bienes_juridicos_states_none_were_identified():
    texto = build_bienes_juridicos_texto(
        "Santa María del Oro", "de julio de 2025 a junio de 2026", [], _fmt
    )

    assert "no se identificaron bienes jurídicos afectados" in texto


def test_single_bien_juridico_uses_singular_wording():
    casos = [{"bien_afectado": "la familia", "total": 3}]
    texto = build_bienes_juridicos_texto(
        "Santa María del Oro", "de julio de 2025 a junio de 2026", casos, _fmt
    )

    assert "el único bien jurídico afectado fue: la familia." in texto
    assert "los tres" not in texto
    assert "los dos" not in texto
    assert "100.00" not in texto


def test_two_bienes_juridicos_use_pair_wording():
    casos = [
        {"bien_afectado": "la familia", "total": 6},
        {"bien_afectado": "el patrimonio", "total": 4},
    ]
    texto = build_bienes_juridicos_texto(
        "Santa María del Oro", "de julio de 2025 a junio de 2026", casos, _fmt
    )

    assert "los dos principales bienes jurídicos afectados fueron" in texto
    assert "la familia (60.00\\,\\%)" in texto
    assert "el patrimonio (40.00\\,\\%)" in texto


def test_three_or_more_bienes_juridicos_keep_original_wording():
    casos = [
        {"bien_afectado": "la familia", "total": 5},
        {"bien_afectado": "el patrimonio", "total": 3},
        {"bien_afectado": "la libertad", "total": 2},
        {"bien_afectado": "otros bienes", "total": 1},
    ]
    texto = build_bienes_juridicos_texto(
        "Santa María del Oro", "de julio de 2025 a junio de 2026", casos, _fmt
    )

    assert "los tres principales bienes jurídicos afectados fueron" in texto
    assert "otros bienes" not in texto


def test_no_delitos_states_none_were_identified():
    texto = build_delitos_texto([], _fmt_int)

    assert "No se identificaron subtipos de delitos" in texto


def test_single_delito_uses_singular_wording():
    casos = [{"delito": "Violencia familiar", "total": 1}]
    texto = build_delitos_texto(casos, _fmt_int)

    assert (
        "el único subtipo de delito con carpetas de investigación fue: "
        "Violencia familiar, con 1." in texto
    )
    assert "segundo puesto" not in texto
    assert "\\ND" not in texto


def test_two_delitos_use_pair_wording():
    casos = [
        {"delito": "Violencia familiar", "total": 5},
        {"delito": "Robo a casa habitación", "total": 3},
    ]
    texto = build_delitos_texto(casos, _fmt_int)

    assert (
        "los dos subtipos de delitos con más carpetas de investigación fueron" in texto
    )
    assert "Violencia familiar, con 5; y Robo a casa habitación, con 3." in texto
    assert "\\ND" not in texto


def test_three_or_more_delitos_keep_original_wording():
    casos = [
        {"delito": "Violencia familiar", "total": 5},
        {"delito": "Robo a casa habitación", "total": 3},
        {"delito": "Amenazas", "total": 2},
        {"delito": "Fraude", "total": 1},
    ]
    texto = build_delitos_texto(casos, _fmt_int)

    assert "en segundo puesto se encuentra Robo a casa habitación, con 3" in texto
    assert "seguido de Amenazas, con 2" in texto
    assert "Fraude" not in texto
