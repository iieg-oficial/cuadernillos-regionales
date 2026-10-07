import pytest

from core.utils.municipalities import (
    get_all_municipio_ids,
    get_municipio_nombre,
    get_region,
)
from core.utils.regions import (
    get_all_region_claves,
    get_all_regions,
    get_region_by_clave,
    get_region_slug,
    normalize_clave,
)


def test_claves_completas_y_ordenadas():
    assert get_all_region_claves() == [f"{i:02d}" for i in range(1, 13)]


def test_ciento_veinticinco_municipios_unicos():
    ids = get_all_municipio_ids()
    assert len(ids) == 125
    assert len(set(ids)) == 125


def test_representante_pertenece_a_su_region():
    for region in get_all_regions():
        assert region.representante in [m["id"] for m in region.municipios]


def test_clave_se_normaliza():
    assert normalize_clave("8") == "08"
    assert normalize_clave("08") == "08"


def test_clave_invalida():
    with pytest.raises(ValueError):
        normalize_clave("13")
    with pytest.raises(ValueError):
        normalize_clave("norte")


def test_region_por_clave():
    region = get_region_by_clave("8")
    assert region.nombre == "Norte"
    assert region.clave == "08"


def test_slugs():
    assert get_region_slug("8") == "08_norte"
    assert get_region_slug("4") == "04_cienega"
    assert get_region_slug("5") == "05_costa-sierra_occidental"


def test_compatibilidad_municipios():
    assert get_region("39") == "Centro"
    assert get_municipio_nombre("39") == "Guadalajara"
