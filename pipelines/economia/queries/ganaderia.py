from sqlalchemy import text
from sqlalchemy.orm import Session


def get_valor_produccion_ganadera_anual(session: Session, cve_mun: int):
    stmt = text("""
        SELECT
            g.anio,
            ROUND(SUM(g.valor_produccion)::numeric / 1000, 2) AS valor_millones
        FROM public.stg_ganadera g
        JOIN public.cat_productos p ON p.id = g.producto_id
        WHERE g.entidad_id = 14
          AND g.municipio_id = :cve_mun
          AND g.valor_produccion IS NOT NULL
          AND p.producto <> 'Ganado En Pie'
        GROUP BY g.anio
        ORDER BY g.anio
    """)
    rows = session.execute(stmt, {"cve_mun": cve_mun}).fetchall()
    return [{"anio": r.anio, "valor_millones": float(r.valor_millones)} for r in rows]


def get_valor_produccion_ganadera_estatal(session: Session, anio: int):
    stmt = text("""
        SELECT ROUND(SUM(g.valor_produccion)::numeric / 1000, 2) AS valor_mdp
        FROM public.stg_ganadera g
        JOIN public.cat_productos p ON p.id = g.producto_id
        WHERE g.entidad_id = 14
          AND g.anio = :anio
          AND g.valor_produccion IS NOT NULL
          AND p.producto <> 'Ganado En Pie'
    """)
    row = session.execute(stmt, {"anio": anio}).fetchone()
    return float(row.valor_mdp) if row and row.valor_mdp else None


def get_valor_produccion_ganadera_municipal(session: Session, cve_mun: int, anio: int):
    stmt = text("""
        SELECT ROUND(SUM(g.valor_produccion)::numeric / 1000, 2) AS valor_mdp
        FROM public.stg_ganadera g
        JOIN public.cat_productos p ON p.id = g.producto_id
        WHERE g.entidad_id = 14
          AND g.municipio_id = :cve_mun
          AND g.anio = :anio
          AND g.valor_produccion IS NOT NULL
          AND p.producto <> 'Ganado En Pie'
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
