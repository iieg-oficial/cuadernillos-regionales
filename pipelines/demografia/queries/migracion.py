from sqlalchemy import text
from sqlalchemy.orm import Session


def get_iim_jalisco(session: Session, fecha: int) -> list[dict]:
    view = {
        2010: "view_iim_municipios_jalisco_2010",
        2020: "view_iim_municipios_jalisco_2020",
    }.get(fecha)
    if not view:
        return []
    index_col = "iaim" if fecha == 2010 else "iim_dp2"
    grado_col = "gaim" if fecha == 2010 else "gim_dp2"
    stmt = text(f"""
        SELECT v.municipio_id, v.municipio, v.viv_totales, v.por_viv_remesas,
               v.por_viv_emigrantes, v.por_viv_reto,
               i.por_viv_circ,
               v.{index_col} AS iim, v.{grado_col} AS grado,
               v.lugar_contexto_nacional, v.lugar_entidad
        FROM {view} v
        JOIN iim_municipal i ON i.municipio_id = v.municipio_id AND i.fecha = :fecha
    """)
    rows = session.execute(stmt, {"fecha": fecha}).fetchall()
    return [dict(r._mapping) for r in rows]


def get_iim_estados(session: Session, fecha: int) -> list[dict]:
    stmt = text("""
        SELECT entidad_id, viv_totales, por_viv_remesas, por_viv_emigrantes,
               por_viv_circ, por_viv_reto, iim_dp2 AS iim, gim_dp2 AS grado,
               lugar_contexto_nacional
        FROM iim_estatal
        WHERE fecha = :fecha
        ORDER BY iim_dp2 DESC
    """)
    rows = session.execute(stmt, {"fecha": fecha}).fetchall()
    return [dict(r._mapping) for r in rows]
