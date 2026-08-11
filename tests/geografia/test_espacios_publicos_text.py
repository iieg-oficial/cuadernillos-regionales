import pytest

from pipelines.geografia.helpers.context import build_espacios_publicos_text
from pipelines.geografia.helpers.formatting import conjunction_before


def _rows(*categorias):
    return [
        {"categoria": nombre, "porcentaje": pct, "orden_pct": orden}
        for orden, (nombre, pct) in enumerate(categorias)
    ]


@pytest.mark.parametrize(
    "palabra,esperado",
    [
        ("centro comercial", "y"),
        ("plaza", "y"),
        ("mercado", "y"),
        ("instalación gubernamental", "e"),
        ("instalación deportiva o recreativa", "e"),
        ("Instalación de Servicios", "e"),
        ("iglesia", "e"),
        ("hielo", "y"),
        ("hierro", "y"),
        ("", "y"),
        (None, "y"),
    ],
)
def test_conjunction_before_follows_spanish_rule(palabra, esperado):
    assert conjunction_before(palabra) == esperado


def test_third_category_starting_with_i_uses_e():
    texto = build_espacios_publicos_text(
        "Acatic",
        9,
        _rows(
            ("Instalación de Servicios", "74.05"),
            ("Plaza", "14.88"),
            ("Instalación Gubernamental", "4.72"),
        ),
    )

    assert "14.88 \\% e instalación gubernamental" in texto


def test_third_category_starting_with_consonant_uses_y():
    texto = build_espacios_publicos_text(
        "Acatic",
        9,
        _rows(
            ("Instalación de Servicios", "74.05"),
            ("Plaza", "14.88"),
            ("Centro Comercial", "4.72"),
        ),
    )

    assert "14.88 \\% y centro comercial" in texto


def test_no_comma_before_the_conjunction():
    texto = build_espacios_publicos_text(
        "Acatic",
        9,
        _rows(("Plaza", "60.00"), ("Mercado", "30.00"), ("Centro Comercial", "10.00")),
    )

    assert "\\%, y " not in texto
    assert "\\%, e " not in texto
