from sqlalchemy import text
from sqlalchemy.orm import Session


def get_nombre_municipio(session: Session, cve_mun: int) -> str:
    stmt = text("""
        SELECT m.nomgeo
        FROM cvegeo_municipalities m
        WHERE m.cve_mun = :cve_mun AND m.cve_ent = 14
        LIMIT 1
    """)
    row = session.execute(stmt, {"cve_mun": cve_mun}).fetchone()
    return row.nomgeo if row else str(cve_mun)


def get_ultima_actualizacion(session: Session):
    stmt = text("""
        SELECT fecha_actualizacion
        FROM actualizaciones
        ORDER BY fecha_actualizacion DESC
        LIMIT 1
    """)
    row = session.execute(stmt).fetchone()
    return row.fecha_actualizacion if row else None


def get_unidades_por_sector_y_rango(session: Session, cve_mun: int):
    stmt = text("""
        WITH base AS (
            SELECT
                CASE (ae.id / 10000)
                    WHEN 11 THEN 'Agricultura, cría y explotación de animales, aprovechamiento forestal, pesca y caza'
                    WHEN 22 THEN 'Generación, transmisión, distribución y comercialización de energía eléctrica, suministro de agua y de gas natural por ductos al consumidor final'
                    WHEN 31 THEN 'Industrias manufactureras'
                    WHEN 32 THEN 'Industrias manufactureras'
                    WHEN 33 THEN 'Industrias manufactureras'
                    WHEN 43 THEN 'Comercio al por mayor'
                    WHEN 46 THEN 'Comercio al por menor'
                    WHEN 48 THEN 'Transportes, correos y almacenamiento'
                    WHEN 49 THEN 'Transportes, correos y almacenamiento'
                    WHEN 51 THEN 'Información en medios masivos'
                    WHEN 52 THEN 'Servicios financieros y de seguros'
                    WHEN 53 THEN 'Servicios inmobiliarios y de alquiler de bienes muebles e intangibles'
                    WHEN 54 THEN 'Servicios profesionales, científicos y técnicos'
                    WHEN 56 THEN 'Servicios de apoyo a los negocios y manejo de residuos, y servicios de remediación'
                    WHEN 61 THEN 'Servicios educativos'
                    WHEN 62 THEN 'Servicios de salud y de asistencia social'
                    WHEN 71 THEN 'Servicios de esparcimiento culturales y deportivos, y otros servicios recreativos'
                    WHEN 72 THEN 'Servicios de alojamiento temporal y de preparación de alimentos y bebidas'
                    WHEN 81 THEN 'Otros servicios excepto actividades gubernamentales'
                    WHEN 93 THEN 'Actividades legislativas, gubernamentales, de impartición de justicia y de organismos internacionales y extraterritoriales'
                    ELSE 'Otro'
                END AS sector,
                rp.descripcion AS rango_personal,
                rp.id AS rango_id
            FROM establecimientos e
            JOIN actualizaciones a ON e.actualizacion_id = a.id
            JOIN localidades l ON e.localidad_id = l.id
            JOIN actividades_economicas ae ON e.actividad_economica_id = ae.id
            JOIN rangos_personal rp ON e.rango_personal_id = rp.id
            WHERE l.municipio_id = :cve_mun
              AND l.entidad_id = 14
              AND a.fecha_actualizacion = (
                  SELECT MAX(fecha_actualizacion) FROM actualizaciones
              )
        )
        SELECT sector, rango_personal, rango_id, COUNT(*) AS total
        FROM base
        GROUP BY sector, rango_personal, rango_id
        ORDER BY sector, rango_id
    """)
    rows = session.execute(stmt, {"cve_mun": cve_mun}).fetchall()
    return [
        {
            "sector": r.sector,
            "rango_personal": r.rango_personal,
            "total": r.total,
        }
        for r in rows
    ]


def get_total_estatal_unidades(session: Session):
    stmt = text("""
        SELECT COUNT(*) AS total
        FROM establecimientos e
        JOIN actualizaciones a ON e.actualizacion_id = a.id
        JOIN localidades l ON e.localidad_id = l.id
        WHERE l.entidad_id = 14
          AND a.fecha_actualizacion = (
              SELECT MAX(fecha_actualizacion) FROM actualizaciones
          )
    """)
    row = session.execute(stmt).fetchone()
    return row.total if row else 0


def get_ranking_municipio_unidades(session: Session, cve_mun: int):
    stmt = text("""
        WITH conteos AS (
            SELECT
                l.municipio_id,
                COUNT(*) AS total
            FROM establecimientos e
            JOIN actualizaciones a ON e.actualizacion_id = a.id
            JOIN localidades l ON e.localidad_id = l.id
            WHERE l.entidad_id = 14
              AND a.fecha_actualizacion = (
                  SELECT MAX(fecha_actualizacion) FROM actualizaciones
              )
            GROUP BY l.municipio_id
        ),
        ranked AS (
            SELECT municipio_id, total,
                   RANK() OVER (ORDER BY total DESC) AS posicion
            FROM conteos
        )
        SELECT posicion
        FROM ranked
        WHERE municipio_id = :cve_mun
    """)
    row = session.execute(stmt, {"cve_mun": cve_mun}).fetchone()
    return row.posicion if row else None
