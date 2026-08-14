import json
from pathlib import Path

import pytest

from core.utils.municipalities import get_municipio_nombre
from pipelines.directorio_municipal.extract import CATALOG_PATH, Extract, _normalize

TOTAL_MUNICIPIOS = 125


@pytest.fixture(scope="module")
def catalogo():
    return json.loads(Path(CATALOG_PATH).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "municipio_id,esperado",
    [
        ("1", "Acatic"),
        ("12", "Atenguillo"),
        ("39", "Guadalajara"),
        ("107", "Tuxcueca"),
        ("120", "Zapopan"),
        ("125", "San Ignacio Cerro Gordo"),
    ],
)
def test_extract_returns_the_requested_municipio(municipio_id, esperado):
    record = Extract().execute(municipio_id)

    assert _normalize(record["municipio"]) == _normalize(esperado)


def test_every_municipio_resolves_to_itself():
    for clave in range(1, TOTAL_MUNICIPIOS + 1):
        nombre = get_municipio_nombre(clave)
        record = Extract().execute(str(clave))
        assert _normalize(record["municipio"]) == _normalize(nombre), (
            f"clave {clave}: se esperaba {nombre}, llegó {record['municipio']}"
        )


def test_catalog_ids_match_the_project_keys(catalogo):
    desalineados = [
        (row["id"], row["municipio"])
        for row in catalogo
        if _normalize(get_municipio_nombre(row["id"])) != _normalize(row["municipio"])
    ]

    assert desalineados == []


def test_catalog_has_one_record_per_municipio(catalogo):
    claves = [row["id"] for row in catalogo]

    assert len(claves) == TOTAL_MUNICIPIOS
    assert sorted(claves) == list(range(1, TOTAL_MUNICIPIOS + 1))


def test_unknown_municipio_raises():
    with pytest.raises(ValueError):
        Extract().execute("999")
