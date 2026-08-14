from calendar import monthrange
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def _end_of_month(year, month):
    _, last_day = monthrange(year, month)
    return date(year, month, last_day)


def get_ultimo_corte(session: Session):
    stmt = text("SELECT MAX(fecha_corte) AS fecha FROM stg_asg_imss")
    row = session.execute(stmt).fetchone()
    return row.fecha if row else None


def get_fechas_comparacion(fecha_corte):
    m = fecha_corte.month
    return (
        fecha_corte,
        _end_of_month(fecha_corte.year - 1, m),
        _end_of_month(fecha_corte.year - 2, m),
    )


def get_asegurados_municipio(session: Session, cvegeo, t0, t1, t2):
    stmt = text("""
        SELECT
            COALESCE(SUM(CASE WHEN fecha_corte = :t0
                THEN asegurados END), 0) AS total_t0,
            COALESCE(SUM(CASE WHEN fecha_corte = :t1
                THEN asegurados END), 0) AS total_t1,
            COALESCE(SUM(CASE WHEN fecha_corte = :t2
                THEN asegurados END), 0) AS total_t2
        FROM vw_asg_imss
        WHERE cvegeo = :cvegeo
          AND sector_economico_4 IS NOT NULL
          AND fecha_corte IN (:t0, :t1, :t2)
    """)
    row = session.execute(
        stmt, {"cvegeo": cvegeo, "t0": t0, "t1": t1, "t2": t2}
    ).fetchone()
    return {"t0": row.total_t0, "t1": row.total_t1, "t2": row.total_t2}


def sumar_asegurados_estatal(por_municipio, clave="t0"):
    return sum(r[clave] for r in por_municipio)


def get_asegurados_por_division(session: Session, cvegeo, t0, t1, t2):
    stmt = text("""
        SELECT
            REPLACE(s1.descripcion, 'Div-', '') AS division,
            COALESCE(SUM(
                CASE WHEN v.fecha_corte = :t0 THEN v.asegurados END
            ), 0) AS total_t0,
            COALESCE(SUM(
                CASE WHEN v.fecha_corte = :t1 THEN v.asegurados END
            ), 0) AS total_t1,
            COALESCE(SUM(
                CASE WHEN v.fecha_corte = :t2 THEN v.asegurados END
            ), 0) AS total_t2
        FROM vw_asg_imss v
        JOIN cat_sector_1 s1 ON v.sector_economico_1 = s1.clave
        WHERE v.cvegeo = :cvegeo
          AND v.fecha_corte IN (:t0, :t1, :t2)
        GROUP BY s1.descripcion
        ORDER BY total_t0 DESC
    """)
    rows = session.execute(
        stmt, {"cvegeo": cvegeo, "t0": t0, "t1": t1, "t2": t2}
    ).fetchall()
    return [
        {"division": r.division, "t0": r.total_t0, "t1": r.total_t1, "t2": r.total_t2}
        for r in rows
    ]


def get_asegurados_todos_municipios(session: Session, t0, t1):
    stmt = text("""
        SELECT
            cvegeo,
            COALESCE(SUM(
                CASE WHEN fecha_corte = :t0 THEN asegurados END
            ), 0) AS total_t0,
            COALESCE(SUM(
                CASE WHEN fecha_corte = :t1 THEN asegurados END
            ), 0) AS total_t1
        FROM vw_asg_imss
        WHERE fecha_corte IN (:t0, :t1)
          AND sector_economico_4 IS NOT NULL
        GROUP BY cvegeo
        ORDER BY total_t0 DESC
    """)
    rows = session.execute(stmt, {"t0": t0, "t1": t1}).fetchall()
    return [{"cvegeo": r.cvegeo, "t0": r.total_t0, "t1": r.total_t1} for r in rows]
