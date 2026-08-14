import pytest

from pipelines.geografia.helpers.formatting import title_case_es
from pipelines.geografia.helpers.tables import health_institution_label

ISSSTE_RAW = (
    "Instituto De Seguridad Y Servicios Sociales De Los Trabajadores Del Estado"
)
ISSSTE_LABEL = (
    "Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado"
)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("SECRETARIA DE SALUD", "Secretaria de Salud"),
        (
            "instituto mexicano del seguro social",
            "Instituto Mexicano del Seguro Social",
        ),
        (
            "Sistema Nacional Para El Desarrollo Integral De La Familia",
            "Sistema Nacional para el Desarrollo Integral de la Familia",
        ),
        (
            "Instituto De Seguridad Y Servicios Sociales",
            "Instituto de Seguridad y Servicios Sociales",
        ),
        ("De Los Reyes", "De los Reyes"),
    ],
)
def test_title_case_keeps_spanish_connectors_lowercase(value, expected):
    assert title_case_es(value) == expected


@pytest.mark.parametrize("value", [None, "", "ND"])
def test_title_case_passes_through_missing_values(value):
    assert title_case_es(value) == value


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Secretaria De Salud", "Secretaría de Salud"),
        (
            "Secretaria De Comunicaciones Y Transportes",
            "Secretaría de Comunicaciones y Transportes",
        ),
        ("Secretaria De La Defensa Nacional", "Secretaría de la Defensa Nacional"),
        (
            "Instituto Mexicano Del Seguro Social",
            "Instituto Mexicano del Seguro Social",
        ),
        (ISSSTE_RAW, ISSSTE_LABEL),
        ("Petroleos Mexicanos", "Petróleos Mexicanos"),
        ("Centros De Integracion Juvenil", "Centros de integración juvenil"),
        (
            "Sistema Nacional Para El Desarrollo Integral De La Familia",
            "Sistema Nacional para el Desarrollo Integral de la Familia",
        ),
    ],
)
def test_known_institutions_render_with_accents_and_title_case(raw, expected):
    assert health_institution_label(raw) == expected


def test_unknown_institution_falls_back_to_title_case():
    assert health_institution_label("Hospital De La Ninez") == "Hospital de la Ninez"
