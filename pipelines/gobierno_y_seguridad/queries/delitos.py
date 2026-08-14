from sqlalchemy import text
from sqlalchemy.orm import Session


def get_anios_disponibles(session: Session) -> list[int]:
    stmt = text("""
        SELECT anio
        FROM vw_delitos_comparables_general
        WHERE clave_ent = '14'
        GROUP BY anio
        HAVING COUNT(DISTINCT mes) = 12
        ORDER BY anio DESC
        LIMIT 2
    """)
    return [row.anio for row in session.execute(stmt)]


def get_conteo_por_municipio_anio(
    session: Session, anio_anterior: int, anio_actual: int
) -> list[dict]:
    stmt = text("""
        SELECT cve_municipio, municipio, anio, SUM(conteo) AS total
        FROM vw_delitos_comparables_general
        WHERE clave_ent = '14'
          AND anio IN (:anio_anterior, :anio_actual)
        GROUP BY cve_municipio, municipio, anio
        ORDER BY cve_municipio, anio
    """)
    rows = session.execute(
        stmt, {"anio_anterior": anio_anterior, "anio_actual": anio_actual}
    )
    return [
        {
            "cvegeo": row.cve_municipio,
            "municipio": row.municipio,
            "anio": row.anio,
            "total": row.total,
        }
        for row in rows
    ]
