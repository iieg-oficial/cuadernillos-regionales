from sqlalchemy import text
from sqlalchemy.orm import Session


def get_ultima_actualizacion(session: Session):
    stmt = text("""
        SELECT id, fecha_actualizacion
        FROM cat_actualizaciones
        ORDER BY fecha_actualizacion DESC
        LIMIT 1
    """)
    row = session.execute(stmt).fetchone()
    return row if row else None


def get_unidades_por_sector_y_rango(session: Session, cve_mun: int, act_id: int):
    stmt = text("""
        SELECT s.sector, rp.descripcion AS rango_personal, rp.id AS rango_id,
               COUNT(*) AS total
        FROM stg_est_jal e
        JOIN cat_localidades l ON e.localidad_id = l.id
        JOIN cat_sectores s ON e.sector_id = s.id
        JOIN cat_rangos_personal rp ON e.rango_personal_id = rp.id
        WHERE e.actualizacion_id = :act_id
          AND l.municipio_id = :cve_mun
        GROUP BY s.sector, rp.descripcion, rp.id
        ORDER BY s.sector, rp.id
    """)
    rows = session.execute(stmt, {"cve_mun": cve_mun, "act_id": act_id}).fetchall()
    return [
        {
            "sector": r.sector,
            "rango_personal": r.rango_personal,
            "total": r.total,
        }
        for r in rows
    ]


def get_ranking_y_total_estatal(session: Session, cve_mun: int, act_id: int):
    stmt = text("""
        WITH conteos AS (
            SELECT
                l.municipio_id,
                COUNT(*) AS total
            FROM stg_est_jal e
            JOIN cat_localidades l ON e.localidad_id = l.id
            WHERE e.actualizacion_id = :act_id
            GROUP BY l.municipio_id
        ),
        ranked AS (
            SELECT
                municipio_id,
                total,
                SUM(total) OVER () AS total_estatal,
                RANK() OVER (ORDER BY total DESC) AS posicion
            FROM conteos
        )
        SELECT total_estatal, posicion
        FROM ranked
        WHERE municipio_id = :cve_mun
    """)
    row = session.execute(stmt, {"cve_mun": cve_mun, "act_id": act_id}).fetchone()
    if row:
        return row.total_estatal, row.posicion
    return 0, None
