from sqlalchemy import text
from sqlalchemy.orm import Session


def get_pobreza_municipio(session: Session, cve_mun: str, anio: int) -> dict | None:
    stmt = text("""
        SELECT *
        FROM stg_pobreza_multidimensional_datos
        WHERE cve_mun = :cve_mun AND anio = :anio
    """)
    row = session.execute(stmt, {"cve_mun": cve_mun, "anio": anio}).fetchone()
    return dict(row._mapping) if row else None


def get_pobreza_por_entidad(session: Session, anio: int) -> list[dict]:
    stmt = text("""
        SELECT
            LEFT(cve_mun, 2) AS cve_ent,
            SUM(pobreza_personas)::float / NULLIF(SUM(poblacion), 0) * 100   AS pobreza_porcentaje,
            SUM(pobreza_ext_personas)::float / NULLIF(SUM(poblacion), 0) * 100 AS pobreza_ext_porcentaje
        FROM stg_pobreza_multidimensional_datos
        WHERE anio = :anio
          AND poblacion IS NOT NULL
          AND pobreza_personas IS NOT NULL
        GROUP BY LEFT(cve_mun, 2)
        ORDER BY pobreza_porcentaje DESC
    """)
    rows = session.execute(stmt, {"anio": anio}).fetchall()
    return [dict(r._mapping) for r in rows]


def get_pobreza_jalisco(session: Session, anio: int) -> list[dict]:
    stmt = text("""
        SELECT *
        FROM stg_pobreza_multidimensional_datos
        WHERE cve_mun LIKE '14%' AND anio = :anio
        ORDER BY pobreza_porcentaje DESC
    """)
    rows = session.execute(stmt, {"anio": anio}).fetchall()
    return [dict(r._mapping) for r in rows]
