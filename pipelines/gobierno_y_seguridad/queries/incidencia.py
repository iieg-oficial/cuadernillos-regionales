from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.orm import Session

MES_A_NUMERO = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12,
}

NUM_MESES = 12


def get_ventana_ultimos_meses(
    session: Session, num_meses: int = NUM_MESES
) -> list[tuple]:
    stmt = text("""
        SELECT DISTINCT anio, mes
        FROM v_delitos_comparables_general
        WHERE clave_ent = '14'
    """)
    indices = [
        row.anio * 12 + (MES_A_NUMERO[row.mes] - 1)
        for row in session.execute(stmt)
        if row.mes in MES_A_NUMERO
    ]
    if not indices:
        return []
    last_idx = max(indices)
    start_idx = last_idx - (num_meses - 1)
    return [(idx // 12, idx % 12 + 1) for idx in range(start_idx, last_idx + 1)]


def get_carpetas_por_mes(
    session: Session, cve_municipio: str, ventana: list[tuple]
) -> list[dict]:
    if not ventana:
        return []
    anios = tuple(sorted({anio for anio, _ in ventana}))
    stmt = text("""
        SELECT anio, mes, SUM(conteo) AS total
        FROM v_delitos_comparables_general
        WHERE cve_municipio = :cve_municipio
          AND anio IN :anios
        GROUP BY anio, mes
    """)
    rows = session.execute(stmt, {"cve_municipio": cve_municipio, "anios": anios})
    totales = {}
    for row in rows:
        mes_num = MES_A_NUMERO.get(row.mes)
        if mes_num:
            totales[(row.anio, mes_num)] = row.total
    return [
        {"anio": anio, "mes": mes, "total": totales.get((anio, mes), 0)}
        for anio, mes in ventana
    ]


def get_casos_por_bien_afectado(
    session: Session, cve_municipio: str, ventana: list[tuple]
) -> list[dict]:
    if not ventana:
        return []
    anios = tuple(sorted({anio for anio, _ in ventana}))
    window = set(ventana)
    stmt = text("""
        SELECT anio, mes, bien_juridico_afectado, SUM(conteo) AS total
        FROM v_delitos_comparables_general
        WHERE cve_municipio = :cve_municipio
          AND anio IN :anios
        GROUP BY anio, mes, bien_juridico_afectado
    """)
    rows = session.execute(stmt, {"cve_municipio": cve_municipio, "anios": anios})
    agg = defaultdict(int)
    for row in rows:
        mes_num = MES_A_NUMERO.get(row.mes)
        if mes_num and (row.anio, mes_num) in window:
            agg[row.bien_juridico_afectado] += row.total
    return sorted(
        [{"bien_afectado": bien, "total": total} for bien, total in agg.items()],
        key=lambda r: r["total"],
        reverse=True,
    )


def get_casos_por_delito(
    session: Session, cve_municipio: str, ventana: list[tuple]
) -> list[dict]:
    if not ventana:
        return []
    anios = tuple(sorted({anio for anio, _ in ventana}))
    window = set(ventana)
    stmt = text("""
        SELECT anio, mes, subtipo_delito, SUM(conteo) AS total
        FROM v_delitos_comparables_general
        WHERE cve_municipio = :cve_municipio
          AND anio IN :anios
          AND subtipo_delito NOT ILIKE 'Otros%'
        GROUP BY anio, mes, subtipo_delito
    """)
    rows = session.execute(stmt, {"cve_municipio": cve_municipio, "anios": anios})
    agg = defaultdict(int)
    for row in rows:
        mes_num = MES_A_NUMERO.get(row.mes)
        if mes_num and (row.anio, mes_num) in window:
            agg[row.subtipo_delito] += row.total
    return sorted(
        [{"delito": delito, "total": total} for delito, total in agg.items()],
        key=lambda r: r["total"],
        reverse=True,
    )
