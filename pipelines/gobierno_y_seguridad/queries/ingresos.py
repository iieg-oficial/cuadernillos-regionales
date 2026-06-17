from sqlalchemy import text
from sqlalchemy.orm import Session

CONCEPTOS_INGRESOS_PROPIOS = (
    "Impuestos",
    "Cuotas y Aportaciones de Seguridad Social",
    "Contribuciones de Mejoras",
    "Derechos",
    "Productos",
    "Aprovechamientos",
)


def get_anios_efipem(session: Session) -> list[int]:
    stmt = text("""
        SELECT DISTINCT anio
        FROM vw_efipem
        WHERE cve_ent = 14
          AND tema = 'Ingresos'
          AND clasificador = 'Tema'
          AND concepto = 'Total de ingresos'
        ORDER BY anio DESC
        LIMIT 2
    """)
    return [row.anio for row in session.execute(stmt)]


def get_ingresos_municipales(
    session: Session, anio_actual: int, anio_anterior: int
) -> list[dict]:
    stmt = text("""
        SELECT
            e.cvegeo,
            e.cve_mun,
            e.anio,
            e.clasificador,
            e.concepto,
            e.valor
        FROM vw_efipem e
        WHERE e.cve_ent = 14
          AND e.tema = 'Ingresos'
          AND e.anio IN (:anio_actual, :anio_anterior)
          AND (
            (e.clasificador = 'Tema' AND e.concepto = 'Total de ingresos')
            OR
            (e.clasificador = 'Capítulo' AND e.concepto IN :conceptos)
          )
        ORDER BY e.cvegeo, e.anio
    """)
    rows = session.execute(
        stmt,
        {
            "anio_actual": anio_actual,
            "anio_anterior": anio_anterior,
            "conceptos": CONCEPTOS_INGRESOS_PROPIOS,
        },
    )
    return [
        {
            "cvegeo": row.cvegeo.strip(),
            "cve_mun": row.cve_mun,
            "anio": row.anio,
            "clasificador": row.clasificador,
            "concepto": row.concepto,
            "valor": row.valor,
        }
        for row in rows
    ]
