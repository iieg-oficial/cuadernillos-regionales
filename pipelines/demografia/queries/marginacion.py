from sqlalchemy import text
from sqlalchemy.orm import Session


def get_cvegeo_localidades(session: Session, cve_mun: int) -> dict[int, str]:
    municipio_id = 14000 + cve_mun
    stmt = text("""
        SELECT
            l.id,
            CAST(l.municipio_id AS text) || LPAD(CAST(l.clave_localidad AS text), 4, '0') AS cvegeo
        FROM localidades l
        WHERE l.municipio_id = :municipio_id
          AND l.entidad_id = 14
    """)
    rows = session.execute(stmt, {"municipio_id": municipio_id}).fetchall()
    return {r.id: r.cvegeo for r in rows}


def get_marginacion_localidades(
    session: Session, cve_mun: int, anio: int
) -> list[dict]:
    municipio_id = 14000 + cve_mun
    stmt = text("""
        SELECT
            CAST(l.municipio_id AS text) || LPAD(CAST(l.clave_localidad AS text), 4, '0') AS cvegeo,
            l.localidad,
            gm.grado_marginacion,
            ml.porc_pob15_analfabeta,
            ml.porc_pob15_sin_educ_basica,
            ml.porc_viv_sin_drenaje_ni_excusado,
            ml.porc_viv_sin_energia,
            ml.porc_viv_sin_agua_entubada,
            ml.porc_viv_piso_tierra,
            ml.prom_ocup_por_cuarto,
            ml.porc_viv_sin_refrigerador,
            ml.pob_total
        FROM marginaciones_localidades ml
        JOIN localidades l ON l.id = ml.localidad_id
        LEFT JOIN grados_marginacion gm ON gm.id = ml.grado_marginacion_id
        WHERE l.municipio_id = :municipio_id
          AND l.entidad_id = 14
          AND EXTRACT(YEAR FROM ml.fecha_actualizacion) = :anio
        ORDER BY ml.pob_total DESC
    """)
    rows = session.execute(
        stmt, {"municipio_id": municipio_id, "anio": anio}
    ).fetchall()
    return [{**dict(r._mapping), "cvegeo": r.cvegeo} for r in rows]


def get_marginacion_jalisco(session: Session, anio: int) -> list[dict]:
    stmt = text("""
        SELECT
            mm.municipio_id,
            gm.grado_marginacion,
            mm.pob_total,
            mm.porc_pob15_analfabeta,
            mm.pob15_sin_educ_bas,
            mm.porc_viv_sin_drenaje_ni_excusado,
            mm.porc_viv_sin_energia,
            mm.porc_viv_sin_agua_entubada,
            mm.porc_viv_piso_tierra,
            mm.prom_ocup_por_cuarto,
            mm.porc_pob_loc_menos5000_hab,
            mm.pob_ocup_hasta_2_sal_min,
            mm.indice_marginacion,
            mm.lugar_contexto_nacional,
            mm.porc_viv_sin_refrigerador
        FROM marginaciones_municipales mm
        LEFT JOIN grados_marginacion gm ON gm.id = mm.grado_marginacion_id
        LEFT JOIN cvegeo_municipalities m ON m.cvegeo = mm.municipio_id
        WHERE m.cve_ent = 14
          AND EXTRACT(YEAR FROM mm.fecha_actualizacion) = :anio
        ORDER BY mm.indice_marginacion DESC
    """)
    rows = session.execute(stmt, {"anio": anio}).fetchall()
    return [dict(r._mapping) for r in rows]


def get_marginacion_estatal(
    session: Session, entidad_id: int, anio: int
) -> dict | None:
    stmt = text("""
        SELECT
            gm.grado_marginacion,
            me.pob_total,
            me.porc_pob15_analfabeta,
            me.pob15_sin_educ_bas,
            me.porc_viv_sin_drenaje_ni_excusado,
            me.porc_viv_sin_energia,
            me.porc_viv_sin_agua_entubada,
            me.porc_viv_piso_tierra,
            me.porc_viv_con_hacinamiento,
            me.porc_pob_loc_menos5000_hab,
            me.pob_ocup_hasta_2_sal_min,
            me.porc_viv_sin_refrigerador,
            me.indice_marginacion,
            me.lugar_contexto_nacional
        FROM marginaciones_estatales me
        LEFT JOIN grados_marginacion gm ON gm.id = me.grado_marginacion_id
        WHERE me.entidad_id = :entidad_id
          AND EXTRACT(YEAR FROM me.fecha_actualizacion) = :anio
    """)
    row = session.execute(stmt, {"entidad_id": entidad_id, "anio": anio}).fetchone()
    return dict(row._mapping) if row else None
