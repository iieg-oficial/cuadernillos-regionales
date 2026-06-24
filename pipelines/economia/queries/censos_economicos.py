from sqlalchemy import text
from sqlalchemy.orm import Session

ANIOS_VALIDOS = {2019, 2024}


def get_vacb_por_subsector(session: Session, cve_mun: int, anio: int):
    if anio not in ANIOS_VALIDOS:
        return []

    if anio == 2024:
        stmt = text("""
            SELECT
                actividad_codigo AS codigo,
                actividad AS subsector,
                SUM(valor_agregado_censal_bruto_mdp) AS vacb
            FROM vw_economico_municipal_2024
            WHERE cve_ent = 14
              AND cve_mun = :cve_mun
              AND estrato_id = 1
              AND LENGTH(actividad_codigo) = 3
              AND valor_agregado_censal_bruto_mdp IS NOT NULL
            GROUP BY actividad_codigo, actividad
            ORDER BY vacb DESC NULLS LAST
        """)
    else:
        stmt = text("""
            SELECT
                actividad_codigo AS codigo,
                actividad AS subsector,
                SUM(valor_agregado_censal_bruto_mdp) AS vacb
            FROM vw_economico_municipal_2019
            WHERE cve_ent = 14
              AND cve_mun = :cve_mun
              AND estrato_id = 1
              AND LENGTH(actividad_codigo) = 3
              AND valor_agregado_censal_bruto_mdp IS NOT NULL
            GROUP BY actividad_codigo, actividad
            ORDER BY vacb DESC NULLS LAST
        """)

    rows = session.execute(stmt, {"cve_mun": cve_mun}).fetchall()
    return [
        {"codigo": r.codigo, "subsector": r.subsector, "vacb": r.vacb}
        for r in rows
        if r.vacb is not None
    ]


def get_vacb_total(session: Session, cve_mun: int, anio: int):
    if anio not in ANIOS_VALIDOS:
        return None

    if anio == 2024:
        stmt = text("""
            SELECT SUM(valor_agregado_censal_bruto_mdp) AS vacb_total
            FROM vw_economico_municipal_2024
            WHERE cve_ent = 14
              AND cve_mun = :cve_mun
              AND estrato_id = 1
              AND LENGTH(actividad_codigo) = 3
              AND valor_agregado_censal_bruto_mdp IS NOT NULL
        """)
    else:
        stmt = text("""
            SELECT SUM(valor_agregado_censal_bruto_mdp) AS vacb_total
            FROM vw_economico_municipal_2019
            WHERE cve_ent = 14
              AND cve_mun = :cve_mun
              AND estrato_id = 1
              AND LENGTH(actividad_codigo) = 3
              AND valor_agregado_censal_bruto_mdp IS NOT NULL
        """)

    row = session.execute(stmt, {"cve_mun": cve_mun}).fetchone()
    return row.vacb_total if row and row.vacb_total is not None else None
