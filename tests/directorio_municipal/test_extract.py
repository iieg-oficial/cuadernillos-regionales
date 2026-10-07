import json
from pathlib import Path

import pytest

from core.utils.municipalities import get_municipio_nombre
from core.utils.regions import get_all_regions, get_region_by_clave
from pipelines.directorio_municipal.extract import CATALOG_PATH, Extract, _normalize

TOTAL_MUNICIPIOS = 125


@pytest.fixture(scope="module")
def catalogo():
    return json.loads(Path(CATALOG_PATH).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "region_clave,municipio_esperado",
    [
        ("03", "Acatic"),
        ("05", "Atenguillo"),
        ("01", "Guadalajara"),
        ("11", "Tuxcueca"),
        ("01", "Zapopan"),
        ("03", "San Ignacio Cerro Gordo"),
    ],
)
def test_extract_incluye_municipio_de_la_region(region_clave, municipio_esperado):
    region = get_region_by_clave(region_clave)
    resultado = Extract().execute(region)

    nombres = [m["municipio"] for m in resultado["municipios"]]
    assert municipio_esperado in nombres


def test_every_municipio_resolves_to_itself():
    for region in get_all_regions():
        resultado = Extract().execute(region)
        nombres = [m["municipio"] for m in resultado["municipios"]]
        assert len(resultado["municipios"]) == len(region.municipios)
        for m in region.municipios:
            assert m["municipio"] in nombres, (region.clave, m["municipio"])
        assert nombres == sorted(nombres)
        campos = {
            "municipio",
            "presidente",
            "correo",
            "domicilio",
            "telefono",
            "sindico",
            "regidores",
            "partido",
        }
        for m in resultado["municipios"]:
            assert campos.issubset(m.keys())


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
