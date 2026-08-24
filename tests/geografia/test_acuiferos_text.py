import pytest

from pipelines.geografia.helpers.context import (
    PREAMBULO_ACUIFEROS,
    build_acuiferos_text,
    join_names,
)


@pytest.mark.parametrize(
    "names,expected",
    [
        (["Ameca"], "Ameca"),
        (["Ameca", "Arenal"], "Ameca y Arenal"),
        (["Ameca", "Arenal", "Atemajac"], "Ameca, Arenal y Atemajac"),
    ],
)
def test_join_names_uses_conjunction_before_last_item(names, expected):
    assert join_names(names) == expected


def test_multiple_acuiferos_use_colon_and_conjunction():
    texto = build_acuiferos_text(
        "Ameca, Arenal, Atemajac, Cuquío, San Isidro, Toluquilla", "40.00", "60.00"
    )

    assert texto.startswith(
        f"{PREAMBULO_ACUIFEROS}el territorio está ubicado dentro de los acuíferos: "
        "Ameca, Arenal, Atemajac, Cuquío, San Isidro y Toluquilla."
    )


def test_single_acuifero_uses_singular_without_colon():
    texto = build_acuiferos_text("Ameca", "40.00", "60.00")

    assert texto.startswith(
        f"{PREAMBULO_ACUIFEROS}el territorio está ubicado dentro del acuífero Ameca."
    )
    assert "dentro de los acuíferos" not in texto
    assert "en él" in texto


def test_both_positive_keeps_both_percentages():
    texto = build_acuiferos_text("Ameca, Arenal", "40.00", "60.00")

    assert "Del total de la superficie municipal comprendida en ellos" in texto
    assert "60.00 \\% no tiene disponibilidad" in texto
    assert "40.00 \\% cuenta con disponibilidad" in texto


def test_zero_availability_avoids_zero_percent_wording():
    texto = build_acuiferos_text("Ameca, Arenal", "0.00", "100.00")

    assert (
        "La totalidad de la superficie municipal comprendida en ellos "
        "no cuenta con disponibilidad de agua subterránea." in texto
    )
    assert "0.00" not in texto
    assert "100.00" not in texto


def test_full_availability_avoids_zero_percent_wording():
    texto = build_acuiferos_text("Ameca, Arenal", "100.00", "0.00")

    assert (
        "La totalidad de la superficie municipal comprendida en ellos "
        "cuenta con disponibilidad de agua subterránea." in texto
    )
    assert "no cuenta con disponibilidad" not in texto
    assert "0.00" not in texto


def test_single_acuifero_with_zero_availability_agrees_in_number():
    texto = build_acuiferos_text("Ameca", "0.00", "100.00")

    assert "comprendida en él no cuenta con disponibilidad" in texto
    assert "en ellos" not in texto


@pytest.mark.parametrize("nombres", [None, "", "   ", ","])
def test_missing_names_returns_no_data_sentence(nombres):
    texto = build_acuiferos_text(nombres, "40.00", "60.00")

    assert texto == (
        "No se dispone de información sobre los acuíferos "
        "que abarcan el territorio municipal."
    )


def test_percentages_with_symbol_are_parsed():
    texto = build_acuiferos_text("Ameca, Arenal", "0.00 \\%", "100.00 \\%")

    assert "La totalidad" in texto


def test_unparseable_percentages_omit_availability_sentence():
    texto = build_acuiferos_text("Ameca, Arenal", None, None)

    assert texto == (
        f"{PREAMBULO_ACUIFEROS}el territorio está ubicado dentro de los acuíferos: "
        "Ameca y Arenal."
    )


def test_names_are_trimmed_and_empty_segments_dropped():
    texto = build_acuiferos_text("  Ameca ,  , Arenal  ", "40.00", "60.00")

    assert "los acuíferos: Ameca y Arenal." in texto


def test_sin_clasificacion_reemplaza_totalidad_sin_disponibilidad():
    texto = build_acuiferos_text(
        "Ciénega de Chapala, Tizapán", "0.00", "83.68", "16.32"
    )
    assert "La totalidad" not in texto
    assert "83.68 \\% no cuenta con disponibilidad de agua subterránea" in texto
    assert "16.32 \\% no está clasificado" in texto


def test_sin_clasificacion_reemplaza_totalidad_con_disponibilidad():
    texto = build_acuiferos_text("Ameca, Arenal", "99.74", "0.00", "0.26")
    assert "La totalidad" not in texto
    assert "99.74 \\% cuenta con disponibilidad de agua subterránea" in texto
    assert "0.26 \\% no está clasificado" in texto


def test_sin_clasificacion_se_agrega_al_desglose_completo():
    texto = build_acuiferos_text("Ameca, Arenal", "18.50", "60.19", "21.31")
    assert "60.19 \\% no tiene disponibilidad" in texto
    assert "18.50 \\% cuenta con disponibilidad de agua subterránea" in texto
    assert "21.31 \\% no está clasificado" in texto


def test_sin_clasificacion_en_cero_conserva_la_redaccion_previa():
    texto = build_acuiferos_text("Ameca, Arenal", "0.00", "100.00", "0.00")
    assert (
        "La totalidad de la superficie municipal comprendida en ellos "
        "no cuenta con disponibilidad de agua subterránea." in texto
    )


def test_sin_clasificacion_ausente_conserva_la_redaccion_previa():
    texto = build_acuiferos_text("Ameca, Arenal", "0.00", "100.00")
    assert (
        "La totalidad de la superficie municipal comprendida en ellos "
        "no cuenta con disponibilidad de agua subterránea." in texto
    )


def test_sin_clasificacion_con_un_solo_acuifero_usa_singular():
    texto = build_acuiferos_text("Tizapán", "0.00", "83.68", "16.32")
    assert "comprendida en él" in texto
    assert "en ellos" not in texto
