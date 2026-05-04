from sqlalchemy import text
from sqlalchemy.orm import Session


def get_vacb_por_subsector(session: Session, cve_mun: int, anio: int):
    cve_mun_str = f"{cve_mun:03d}"
    stmt = text("""
        SELECT
            ca.descripcion AS subsector,
            SUM(cd.a111a) AS vacb
        FROM ce_datos cd
        JOIN ce_catalogos_actividades ca ON cd.codigo = ca.codigo
        WHERE cd.anio = :anio
          AND cd.e03 = '14'
          AND cd.e04 = :cve_mun
          AND cd.subsector IS NOT NULL
          AND cd.subsector != ''
          AND cd.id_estrato = ''
        GROUP BY ca.descripcion
        ORDER BY vacb DESC NULLS LAST
    """)
    rows = session.execute(stmt, {"anio": anio, "cve_mun": cve_mun_str}).fetchall()
    return [
        {"subsector": r.subsector, "vacb": r.vacb} for r in rows if r.vacb is not None
    ]


def get_vacb_total(session: Session, cve_mun: int, anio: int):
    cve_mun_str = f"{cve_mun:03d}"
    stmt = text("""
        SELECT SUM(cd.a111a) AS vacb_total
        FROM ce_datos cd
        WHERE cd.anio = :anio
          AND cd.e03 = '14'
          AND cd.e04 = :cve_mun
          AND cd.id_estrato = ''
          AND cd.subsector IS NOT NULL
          AND cd.subsector != ''
    """)
    row = session.execute(stmt, {"anio": anio, "cve_mun": cve_mun_str}).fetchone()
    return row.vacb_total if row else None
