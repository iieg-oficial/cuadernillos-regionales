from sqlalchemy import text
from sqlalchemy.orm import Session


def get_participacion_por_municipio(session: Session) -> list[dict]:
    stmt = text("""
        SELECT
            s.municipio_id,
            m.nomgeo AS municipio,
            s.porc_participacion,
            s.anio
        FROM stg_participacion s
        LEFT JOIN cvegeo_municipalities m
            ON s.municipio_id = m.cve_mun AND s.entidad_id = m.cve_ent
        ORDER BY s.municipio_id, s.anio
    """)
    return [
        {
            "municipio_id": row.municipio_id,
            "municipio": row.municipio,
            "pct": row.porc_participacion,
            "anio": row.anio,
        }
        for row in session.execute(stmt)
    ]
