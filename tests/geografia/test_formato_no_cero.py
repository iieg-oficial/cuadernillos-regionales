import pytest

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
