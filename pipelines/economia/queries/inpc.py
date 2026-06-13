from sqlalchemy import text
from sqlalchemy.orm import Session


def get_inpc_promedio_anual(session: Session, anio: int):
    stmt = text("""
        SELECT AVG(indice_de_precios) AS promedio
        FROM v_inpc_nacional
        WHERE objeto_gasto = 'Índice general'
          AND EXTRACT(YEAR FROM fecha) = :anio
    """)
    row = session.execute(stmt, {"anio": anio}).fetchone()
    return float(row.promedio) if row and row.promedio is not None else None
