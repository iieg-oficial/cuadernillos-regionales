import pytest

from pipelines.geografia.analizer import _pct_desde_superficie
from pipelines.geografia.helpers.formatting import fmt, fmt_no_cero


@pytest.mark.parametrize(
    "valor,esperado",
    [
        (0.001, "0.001"),
        (0.004, "0.004"),
        (0.0049, "0.005"),
    ],
)
def test_usa_tres_decimales_cuando_dos_darian_cero(valor, esperado):
    assert fmt_no_cero(valor) == esperado


@pytest.mark.parametrize("valor", [12.34, 5.6, 100.0, 0.01, 0.005])
def test_conserva_dos_decimales_cuando_el_valor_es_visible(valor):
    assert fmt_no_cero(valor) == fmt(valor)


def test_el_cero_real_sigue_siendo_cero():
    assert fmt_no_cero(0.0) == "0.00"


def test_valor_nulo_se_comporta_como_fmt():
    assert fmt_no_cero(None) == fmt(None)


AREA_KM2 = 362.747


def test_recalcula_el_porcentaje_cuando_viene_en_cero():
    filas = [{"categoria": "Humedales", "superficie_ha": 0.39, "porcentaje": 0}]
    ajustadas = _pct_desde_superficie(filas, AREA_KM2)
    assert fmt_no_cero(ajustadas[0]["porcentaje"]) == "0.001"


def test_no_toca_las_filas_con_porcentaje_visible():
    filas = [{"categoria": "RAMSAR", "superficie_ha": 49.85, "porcentaje": 0.14}]
    assert _pct_desde_superficie(filas, AREA_KM2) == filas


def test_no_recalcula_cuando_la_superficie_tambien_es_cero():
    filas = [{"categoria": "Humedales", "superficie_ha": 0, "porcentaje": 0}]
    assert _pct_desde_superficie(filas, AREA_KM2) == filas


def test_sin_area_municipal_devuelve_las_filas_intactas():
    filas = [{"categoria": "Humedales", "superficie_ha": 0.39, "porcentaje": 0}]
    assert _pct_desde_superficie(filas, None) == filas
