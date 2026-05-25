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


def get_carpetas_por_mes(
    session: Session, cve_municipio: str, anio_anterior: int, anio_actual: int
) -> list[dict]:
    stmt = text("""
        SELECT anio, mes, SUM(conteo) AS total
        FROM v_delitos_comparables_general
        WHERE cve_municipio = :cve_municipio
          AND anio IN (:anio_anterior, :anio_actual)
        GROUP BY anio, mes
        ORDER BY anio, mes
    """)
    rows = session.execute(
        stmt,
        {
            "cve_municipio": cve_municipio,
            "anio_anterior": anio_anterior,
            "anio_actual": anio_actual,
        },
    )
    result = []
    for row in rows:
        mes_num = MES_A_NUMERO.get(row.mes)
        if mes_num:
            result.append({"anio": row.anio, "mes": mes_num, "total": row.total})
    result.sort(key=lambda r: (r["anio"], r["mes"]))
    return result


def get_casos_por_bien_afectado(
    session: Session, cve_municipio: str, anio_anterior: int, anio_actual: int
) -> list[dict]:
    stmt = text("""
        SELECT bien_juridico_afectado, SUM(conteo) AS total
        FROM v_delitos_comparables_general
        WHERE cve_municipio = :cve_municipio
          AND anio IN (:anio_anterior, :anio_actual)
        GROUP BY bien_juridico_afectado
        ORDER BY total DESC
    """)
    rows = session.execute(
        stmt,
        {
            "cve_municipio": cve_municipio,
            "anio_anterior": anio_anterior,
            "anio_actual": anio_actual,
        },
    )
    return [
        {"bien_afectado": row.bien_juridico_afectado, "total": row.total}
        for row in rows
    ]


def get_casos_por_delito(
    session: Session,
    cve_municipio: str,
    bien_afectado: str,
    anio_anterior: int,
    anio_actual: int,
) -> list[dict]:
    stmt = text("""
        SELECT tipo_delito, SUM(conteo) AS total
        FROM v_delitos_comparables_general
        WHERE cve_municipio = :cve_municipio
          AND bien_juridico_afectado = :bien_afectado
          AND anio IN (:anio_anterior, :anio_actual)
        GROUP BY tipo_delito
        ORDER BY total DESC
    """)
    rows = session.execute(
        stmt,
        {
            "cve_municipio": cve_municipio,
            "bien_afectado": bien_afectado,
            "anio_anterior": anio_anterior,
            "anio_actual": anio_actual,
        },
    )
    return [{"delito": row.tipo_delito, "total": row.total} for row in rows]
