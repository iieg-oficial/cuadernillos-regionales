import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core.db import get_session
from core.settings import DatabaseSettings
from pipelines.geografia.analizer import SIN_CLASIFICACION
from pipelines.geografia.helpers.tables import raw_sum

TOLERANCIA = 0.01
TOTAL_MUNICIPIOS = 125

DIMENSIONES = ["acuiferos_situacion", "acuiferos_condicion"]


def _query(dimension):
    return text(f"""
        SELECT nombre, SUM(porcentaje) AS total
        FROM cuadernillos_tab.{dimension}_estadistica_detalle
        GROUP BY nombre
        ORDER BY nombre
    """)


@pytest.fixture(scope="module")
def sumas_por_dimension():
    settings = DatabaseSettings.from_env("cuadernillos_geo")
    try:
        with get_session(settings) as session:
            return {
                dimension: [
                    (r.nombre, r.total) for r in session.execute(_query(dimension))
                ]
                for dimension in DIMENSIONES
            }
    except SQLAlchemyError as exc:
        pytest.skip(f"cuadernillos_geo no disponible: {exc}")


@pytest.mark.parametrize("dimension", DIMENSIONES)
def test_todos_los_municipios_tienen_acuiferos(sumas_por_dimension, dimension):
    assert len(sumas_por_dimension[dimension]) == TOTAL_MUNICIPIOS


@pytest.mark.parametrize("dimension", DIMENSIONES)
def test_porcentaje_de_acuiferos_suma_cien(sumas_por_dimension, dimension):
    desviados = [
        (nombre, total)
        for nombre, total in sumas_por_dimension[dimension]
        if abs(total - 100) > TOLERANCIA
    ]
    assert not desviados, f"Municipios fuera de tolerancia en {dimension}: {desviados}"


FILAS_TABLA = {
    "acuiferos_situacion": [
        ["con disponibilidad"],
        ["sin disponibilidad"],
        SIN_CLASIFICACION,
    ],
    "acuiferos_condicion": [
        ["no explotado", "no sobreexplotado"],
        ["sobreexplotado"],
        SIN_CLASIFICACION,
    ],
}

DETALLE = text("""
    SELECT nombre, categoria, porcentaje
    FROM cuadernillos_tab.{tabla}_estadistica_detalle
""")


@pytest.fixture(scope="module")
def detalle_por_municipio():
    settings = DatabaseSettings.from_env("cuadernillos_geo")
    try:
        with get_session(settings) as session:
            resultado = {}
            for dimension in DIMENSIONES:
                stmt = text(DETALLE.text.format(tabla=dimension))
                agrupado = {}
                for row in session.execute(stmt).mappings():
                    agrupado.setdefault(row["nombre"], []).append(dict(row))
                resultado[dimension] = agrupado
            return resultado
    except SQLAlchemyError as exc:
        pytest.skip(f"cuadernillos_geo no disponible: {exc}")


@pytest.mark.parametrize("dimension", DIMENSIONES)
def test_filas_de_la_tabla_suman_cien(detalle_por_municipio, dimension):
    desviados = []
    for nombre, filas in detalle_por_municipio[dimension].items():
        total = sum(raw_sum(filas, terminos) for terminos in FILAS_TABLA[dimension])
        if abs(total - 100) > TOLERANCIA:
            desviados.append((nombre, round(total, 2)))
    assert not desviados, (
        f"Las filas impresas para {dimension} no cubren el 100 %: {desviados}"
    )
