from sqlalchemy import text
from sqlalchemy.orm import Session


def get_valor_produccion_ganadera_anual(session: Session, cve_mun: int):
    stmt = text("""
        SELECT
            anio,
            ROUND(SUM(valor_produccion)::numeric / 1000000, 2) AS valor_millones
        FROM public.stg_ganadera
        WHERE entidad_id = 14
          AND municipio_id = :cve_mun
          AND valor_produccion IS NOT NULL
        GROUP BY anio
        ORDER BY anio
    """)
    rows = session.execute(stmt, {"cve_mun": cve_mun}).fetchall()
    return [{"anio": r.anio, "valor_millones": float(r.valor_millones)} for r in rows]


def get_valor_produccion_ganadera_estatal(session: Session, anio: int):
    stmt = text("""
        SELECT ROUND(SUM(valor_produccion)::numeric / 1000000, 2) AS valor_mdp
        FROM public.stg_ganadera
        WHERE entidad_id = 14
          AND anio = :anio
          AND valor_produccion IS NOT NULL
    """)
    row = session.execute(stmt, {"anio": anio}).fetchone()
    return float(row.valor_mdp) if row and row.valor_mdp else None


def get_valor_produccion_ganadera_municipal(session: Session, cve_mun: int, anio: int):
    stmt = text("""
        SELECT ROUND(SUM(valor_produccion)::numeric / 1000000, 2) AS valor_mdp
        FROM public.stg_ganadera
        WHERE entidad_id = 14
          AND municipio_id = :cve_mun
          AND anio = :anio
          AND valor_produccion IS NOT NULL
    """)
    row = session.execute(stmt, {"cve_mun": cve_mun, "anio": anio}).fetchone()
    return float(row.valor_mdp) if row and row.valor_mdp else None


def get_ultimo_anio_ganadero(session: Session):
    stmt = text("""
        SELECT MAX(anio) AS anio
        FROM public.stg_ganadera
        WHERE entidad_id = 14
    """)
    row = session.execute(stmt).fetchone()
    return row.anio if row else None
