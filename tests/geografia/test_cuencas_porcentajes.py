import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core.db import get_session
from core.settings import DatabaseSettings

TOLERANCIA = 0.15
BLOQUES = ["cuencas_clasificac", "cuencas_categ"]


def _query(bloque):
    return text(f"""
        SELECT nombre, SUM(porcentaje) AS total, COUNT(*) AS filas
        FROM cuadernillos_tab.{bloque}_estadistica_detalle
        GROUP BY nombre
        ORDER BY nombre
    """)


@pytest.fixture(scope="module")
def sumas_por_bloque():
    settings = DatabaseSettings.from_env("cuadernillos_geo")
    try:
        with get_session(settings) as session:
            return {
                bloque: [
                    (r.nombre, r.total, r.filas)
                    for r in session.execute(_query(bloque))
                ]
                for bloque in BLOQUES
            }
    except SQLAlchemyError as exc:
        pytest.skip(f"cuadernillos_geo no disponible: {exc}")


@pytest.mark.parametrize("bloque", BLOQUES)
def test_cada_bloque_de_la_tabla_suma_cien(sumas_por_bloque, bloque):
    desviados = [
        (nombre, round(total, 2))
        for nombre, total, _ in sumas_por_bloque[bloque]
        if abs(total - 100) > TOLERANCIA
    ]
    assert not desviados, f"Bloque {bloque} fuera de tolerancia: {desviados}"


@pytest.mark.parametrize("bloque", BLOQUES)
def test_ningun_municipio_queda_sin_filas(sumas_por_bloque, bloque):
    vacios = [nombre for nombre, _, filas in sumas_por_bloque[bloque] if filas == 0]
    assert not vacios, f"Municipios sin filas en {bloque}: {vacios}"
