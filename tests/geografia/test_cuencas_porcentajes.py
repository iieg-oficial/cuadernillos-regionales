import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core.db import get_session
from core.settings import DatabaseSettings
from pipelines.geografia.helpers.formatting import sentence_case
from pipelines.geografia.helpers.tables import rows_for

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


COLUMNAS = {
    "categoria": "categoria",
    "superficie_ha": "superficie_ha",
    "porcentaje": "porcentaje",
}

DETALLE = """
    SELECT nombre, categoria, superficie_ha, porcentaje, orden_pct
    FROM cuadernillos_tab.{bloque}_estadistica_detalle
"""


def _to_float(value):
    return float(value.replace("\\,", ""))


@pytest.fixture(scope="module")
def filas_impresas():
    settings = DatabaseSettings.from_env("cuadernillos_geo")
    try:
        with get_session(settings) as session:
            resultado = {}
            for bloque in BLOQUES:
                stmt = text(DETALLE.format(bloque=bloque))
                agrupado = {}
                for row in session.execute(stmt).mappings():
                    agrupado.setdefault(row["nombre"], []).append(dict(row))
                resultado[bloque] = {
                    nombre: rows_for(
                        filas, COLUMNAS, transforms={"categoria": sentence_case}
                    )
                    for nombre, filas in agrupado.items()
                }
            return resultado
    except SQLAlchemyError as exc:
        pytest.skip(f"cuadernillos_geo no disponible: {exc}")


@pytest.mark.parametrize("bloque", BLOQUES)
def test_las_filas_impresas_suman_cien(filas_impresas, bloque):
    desviados = []
    for nombre, filas in filas_impresas[bloque].items():
        total = sum(_to_float(fila["porcentaje"]) for fila in filas)
        if abs(total - 100) > TOLERANCIA:
            desviados.append((nombre, round(total, 2)))
    assert not desviados, (
        f"Las filas impresas de {bloque} no cubren el 100 %: {desviados}"
    )


@pytest.mark.parametrize("bloque", BLOQUES)
def test_no_se_imprime_ninguna_categoria_repetida(filas_impresas, bloque):
    repetidos = {}
    for nombre, filas in filas_impresas[bloque].items():
        categorias = [fila["categoria"] for fila in filas]
        if len(categorias) != len(set(categorias)):
            repetidos[nombre] = categorias
    assert not repetidos, f"Categorías repetidas en {bloque}: {repetidos}"
