from sqlalchemy import text
from sqlalchemy.orm import Session


def get_poblacion_conapo(session: Session, anios: list[int]) -> list[dict]:
    if not anios:
        return []
    stmt = text("""
        SELECT c.cve_mun, v.anio, v.pob_mit_mun AS total
        FROM view_indicadores_demograficos v
        JOIN cvegeo_municipalities c
          ON c.nomgeo = v.municipio AND c.nom_ent = v.entidad
        WHERE v.entidad = 'Jalisco'
          AND v.anio IN :anios
    """)
    rows = session.execute(stmt, {"anios": tuple(anios)})
    return [
        {"cve_mun": row.cve_mun, "anio": row.anio, "total": row.total} for row in rows
    ]
