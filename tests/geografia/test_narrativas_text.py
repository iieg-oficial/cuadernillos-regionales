import pytest

from pipelines.geografia.helpers.context import (
    build_clima_text,
    build_energia_text,
    is_sentinel,
    split_names,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Gasolinera, SIN_DATO", ["Gasolinera"]),
        ("SIN_DATO", []),
        ("Gasolinera, sin_dato, Gas natural", ["Gasolinera", "Gas natural"]),
        ("  Gasolinera ,  , Gas natural ", ["Gasolinera", "Gas natural"]),
        (None, []),
        ("", []),
    ],
)
def test_split_names_drops_sentinels_and_blanks(value, expected):
    assert split_names(value) == expected


def test_energia_without_secondary_types_omits_second_sentence():
    texto = build_energia_text("gasolinera", "1.00", "100.00", "")

    assert texto.endswith("equivalente a 100.00 \\% del total identificado.")
    assert "También se registran" not in texto
    assert "\\ND" not in texto


def test_energia_with_secondary_types_lists_them_with_conjunction():
    texto = build_energia_text(
        "gasolinera", "7.00", "58.33", "Gas L. P. en cilindros, Distribución"
    )

    assert (
        "También se registran Gas L. P. en cilindros y Distribución, "
        "que complementan la red energética municipal." in texto
    )


def test_energia_filters_sentinel_from_list():
    texto = build_energia_text("gasolinera", "126.00", "75.90", "Gas natural, SIN_DATO")

    assert "SIN_DATO" not in texto
    assert "También se registran Gas natural," in texto


def test_energia_with_only_sentinel_omits_second_sentence():
    texto = build_energia_text("gasolinera", "1.00", "100.00", "SIN_DATO")

    assert "También se registran" not in texto
    assert "SIN_DATO" not in texto


@pytest.mark.parametrize("dominante", [None, "", "SIN_DATO"])
def test_energia_without_dominant_type_returns_no_data_sentence(dominante):
    texto = build_energia_text(dominante, "1.00", "100.00", "")

    assert texto == (
        "No se dispone de información sobre unidades económicas "
        "relacionadas con energía para el municipio."
    )


def test_clima_without_other_variants_omits_third_sentence():
    texto = build_clima_text("(A)Ca(w0)", "98.11", "A(C)w0", "1.89", "", None)

    assert "En segundo lugar se presenta A(C)w0 con 1.89 \\%." in texto
    assert "Además se identifican variantes" not in texto
    assert "\\ND" not in texto


def test_clima_without_secondary_omits_second_sentence():
    texto = build_clima_text("(A)Ca(w0)", "100.00", "", None, "", None)

    assert texto == (
        "El municipio presenta un clima predominante de tipo (A)Ca(w0), "
        "que abarca 100.00 \\% del territorio."
    )


def test_clima_with_all_parts_keeps_three_sentences():
    texto = build_clima_text(
        "(A)Ca(w0)", "70.00", "A(C)w0", "20.00", "BS1hw, Cwa", "10.00"
    )

    assert "En segundo lugar" in texto
    assert "Además se identifican variantes como BS1hw y Cwa" in texto
    assert "que representan 10.00 \\%." in texto


@pytest.mark.parametrize("predominante", [None, "", "SIN_DATO"])
def test_clima_without_predominant_returns_no_data_sentence(predominante):
    texto = build_clima_text(predominante, "100.00", "", None, "", None)

    assert texto == (
        "No se dispone de información sobre los tipos de clima "
        "presentes en el municipio."
    )


def test_split_names_ignores_commas_inside_parentheses():
    value = (
        "(A)Ca(w1) (Semicálido templado, con verano cálido, lluvias de verano), "
        "Cb(w2) (Templado, con verano fresco, humedad alta)"
    )

    assert split_names(value) == [
        "(A)Ca(w1) (Semicálido templado, con verano cálido, lluvias de verano)",
        "Cb(w2) (Templado, con verano fresco, humedad alta)",
    ]


def test_clima_conjunction_does_not_corrupt_parenthetical_names():
    value = (
        "A(C)w0 (Semicálido subhúmedo, con lluvias de verano), "
        "Cb(w2) (Templado, con verano fresco, lluvias de verano y humedad alta)"
    )

    texto = build_clima_text("(A)Ca(w0)", "70.00", "A(C)w0", "20.00", value, "10.00")

    assert (
        "Cb(w2) (Templado, con verano fresco, lluvias de verano y humedad alta)"
        in texto
    )
    assert "verano) y Cb(w2)" in texto


@pytest.mark.parametrize("value", ["SIN\\_DATO", "SIN_DATO", "sin\\_dato", "\\ND"])
def test_sentinels_are_detected_after_latex_escaping(value):
    assert is_sentinel(value)


def test_energia_filters_latex_escaped_sentinel():
    texto = build_energia_text(
        "gasolinera", "126.00", "75.90", "Gas natural vehicular, SIN\\_DATO, Gas L. P."
    )

    assert "SIN" not in texto
    assert "También se registran Gas natural vehicular y Gas L. P.," in texto
