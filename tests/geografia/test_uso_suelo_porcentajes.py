import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core.db import get_session
from core.settings import DatabaseSettings

TOLERANCIA = 0.05
TOTAL_MUNICIPIOS = 125

QUERY = text("""
    SELECT nombre, SUM(porcentaje) AS total
    FROM cuadernillos_tab.uso_suelo_estadistica_detalle
    GROUP BY nombre
    ORDER BY nombre
""")


@pytest.fixture(scope="module")
def sumas_por_municipio():
    settings = DatabaseSettings.from_env("cuadernillos_geo")
    try:
        with get_session(settings) as session:
            return [(r.nombre, r.total) for r in session.execute(QUERY)]
    except SQLAlchemyError as exc:
        pytest.skip(f"cuadernillos_geo no disponible: {exc}")


def test_todos_los_municipios_tienen_uso_de_suelo(sumas_por_municipio):
    assert len(sumas_por_municipio) == TOTAL_MUNICIPIOS


def test_porcentaje_de_uso_de_suelo_suma_cien(sumas_por_municipio):
    desviados = [
        (nombre, total)
        for nombre, total in sumas_por_municipio
        if abs(total - 100) > TOLERANCIA
    ]
    assert not desviados, f"Municipios fuera de tolerancia: {desviados}"
