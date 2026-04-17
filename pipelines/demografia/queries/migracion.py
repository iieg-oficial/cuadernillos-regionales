from sqlalchemy import text
from sqlalchemy.orm import Session


def get_iim_municipios(session: Session, fecha: int) -> list[dict]:
    stmt = text("""
        SELECT municipio_id, viv_totales, por_viv_remesas, por_viv_emigrantes,
               por_viv_reto, iim_dp2, lugar_contexto_nacional
        FROM iim_municipal
        WHERE fecha = :fecha
        ORDER BY iim_dp2 DESC
    """)
    rows = session.execute(stmt, {"fecha": fecha}).fetchall()
    return [dict(r._mapping) for r in rows]


def get_iim_estados(session: Session, fecha: int) -> list[dict]:
    stmt = text("""
        SELECT entidad_id, viv_totales, por_viv_remesas, por_viv_emigrantes,
               por_viv_reto, iim_dp2, grado_iim, lugar_contexto_nacional
        FROM iim_estatal
        WHERE fecha = :fecha
        ORDER BY iim_dp2 DESC
    """)
    rows = session.execute(stmt, {"fecha": fecha}).fetchall()
    return [dict(r._mapping) for r in rows]
