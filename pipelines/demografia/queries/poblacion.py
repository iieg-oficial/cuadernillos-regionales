from sqlalchemy import text
from sqlalchemy.orm import Session


def get_nombre_municipio(session: Session, cve_mun: int) -> str:
    stmt = text("""
        SELECT m.nomgeo
        FROM cvegeo_municipalities m
        WHERE m.cve_mun = :cve_mun AND m.cve_ent = 14
        LIMIT 1
    """)
    row = session.execute(stmt, {"cve_mun": cve_mun}).fetchone()
    return row.nomgeo if row else str(cve_mun)


def get_totales_municipio(session: Session, cve_mun: int) -> dict[int, dict]:
    stmt = text("""
        SELECT
            f.fecha,
            p.total,
            p.total_hombres,
            p.total_mujeres
        FROM poblacion p
        JOIN fuentes f ON f.id = p.fuente_id
        WHERE p.municipio_id = :cve_mun
          AND p.entidad_id = 14
          AND p.localidad_id IS NULL
    """)
    rows = session.execute(stmt, {"cve_mun": cve_mun}).fetchall()
    return {
        r.fecha: {
            "total": r.total,
            "hombres": r.total_hombres,
            "mujeres": r.total_mujeres,
        }
        for r in rows
    }


def get_total_estatal(session: Session, anio: int) -> int | None:
    stmt = text("""
        SELECT p.total
        FROM poblacion p
        JOIN fuentes f ON f.id = p.fuente_id
        WHERE p.entidad_id = 14
          AND p.localidad_id IS NULL
          AND p.municipio_id = 0
          AND f.fecha = :anio
    """)
    row = session.execute(stmt, {"anio": anio}).fetchone()
    return row[0] if row else None


def get_total_region(session: Session, cve_muns: list[int], anio: int) -> int | None:
    stmt = text("""
        SELECT SUM(p.total)
        FROM poblacion p
        JOIN fuentes f ON f.id = p.fuente_id
        WHERE p.entidad_id = 14
          AND p.localidad_id IS NULL
          AND p.municipio_id = ANY(:cve_muns)
          AND f.fecha = :anio
    """)
    row = session.execute(stmt, {"cve_muns": cve_muns, "anio": anio}).fetchone()
    return row[0] if row else None


def get_localidades_por_anio(session: Session, cve_mun: int, anio: int) -> list[dict]:
    stmt = text("""
        SELECT l.id, l.localidad, p.total, p.total_hombres, p.total_mujeres
        FROM poblacion p
        JOIN localidades l ON l.id = p.localidad_id
        JOIN fuentes f ON f.id = p.fuente_id
        WHERE p.municipio_id = :cve_mun
          AND p.entidad_id = 14
          AND f.fecha = :anio
        ORDER BY p.total DESC
    """)
    rows = session.execute(stmt, {"cve_mun": cve_mun, "anio": anio}).fetchall()
    return [
        {
            "clave": r.id,
            "localidad": r.localidad,
            "total": r.total,
            "hombres": r.total_hombres,
            "mujeres": r.total_mujeres,
        }
        for r in rows
    ]
