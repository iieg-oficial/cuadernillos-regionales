import pytest

from pipelines.economia.helpers.vacb import (
    build_mayor_crecimiento_text,
    build_subsectores_text,
)

ND = r"\ND"


def _texto(subsectores, pct="75.00\\,\\%", aportacion="1 200.00"):
    return build_subsectores_text(
        subsectores,
        municipio="Zapopan",
        anio=2024,
        pct=pct,
        aportacion=aportacion,
    )


def test_three_subsectores_keep_the_original_wording():
    texto = _texto(["comercio al por menor", "industria alimentaria", "servicios"])

    assert "los tres subsectores más importantes" in texto
    assert (
        "fueron el de comercio al por menor, el de industria alimentaria "
        "y el de servicios" in texto
    )
    assert "generaron en conjunto el 75.00\\,\\% o 1 200.00 millones de pesos" in texto


def test_more_than_three_subsectores_still_describe_only_the_top_three():
    texto = _texto(["comercio", "industria", "servicios", "construcción"])

    assert "los tres subsectores más importantes" in texto
    assert "construcción" not in texto


def test_two_subsectores_use_plural_pair_without_padding():
    texto = _texto(["comercio", "industria"])

    assert "los dos subsectores más importantes" in texto
    assert "fueron el de comercio y el de industria" in texto
    assert "generaron en conjunto" in texto


def test_one_subsector_uses_singular():
    texto = _texto(["comercio"], pct="100.00\\,\\%", aportacion="22.47")

    assert "el subsector más importante" in texto
    assert "fue el de comercio" in texto
    assert "generó el 100.00\\,\\% o 22.47 millones de pesos" in texto
    assert "en conjunto" not in texto


def test_zero_subsectores_explains_inegi_confidentiality():
    texto = build_subsectores_text(
        [], municipio="Santa María del Oro", anio=2024, pct=ND, aportacion=ND
    )

    assert "reservó por confidencialidad" in texto
    assert "Santa María del Oro" in texto
    assert "únicamente se presenta el total" in texto


@pytest.mark.parametrize("subsectores", [[], ["comercio"], ["comercio", "industria"]])
def test_no_wording_ever_leaks_the_nd_macro(subsectores):
    texto = build_subsectores_text(
        subsectores, municipio="Zapopan", anio=2024, pct=ND, aportacion=ND
    )

    assert ND not in texto


def test_mayor_crecimiento_keeps_the_original_wording():
    texto = build_mayor_crecimiento_text(
        subsector="industria alimentaria",
        aportacion_anterior="5.00",
        aportacion_actual="12.00",
        variacion="140.00\\,\\%",
        anio_anterior=2019,
        anio=2024,
    )

    assert "El subsector de industria alimentaria" in texto
    assert "pasando de 5.00 millones de pesos en 2019" in texto
    assert "a 12.00 millones de pesos en 2024" in texto
    assert "una variación del 140.00\\,\\%" in texto


def test_mayor_crecimiento_is_omitted_when_any_figure_is_unavailable():
    texto = build_mayor_crecimiento_text(
        subsector="industria alimentaria",
        aportacion_anterior=ND,
        aportacion_actual="12.00",
        variacion="140.00\\,\\%",
        anio_anterior=2019,
        anio=2024,
    )

    assert texto == ""


def test_mayor_crecimiento_is_omitted_when_there_is_nothing_to_compare():
    texto = build_mayor_crecimiento_text(
        subsector=None,
        aportacion_anterior=None,
        aportacion_actual=None,
        variacion=None,
        anio_anterior=2019,
        anio=2024,
    )

    assert texto == ""
