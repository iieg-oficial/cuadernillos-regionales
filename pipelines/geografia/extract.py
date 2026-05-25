from core.db import get_session
from core.pipelines.stage import Stage
from core.settings import DatabaseSettings
from core.utils.logger import Logger
from pipelines.geografia.helpers.maps import ensure_maps
from pipelines.geografia.queries.clima import (
    get_precipitacion_long,
    get_precipitacion_resumen,
    get_temperatura_long,
    get_temperatura_resumen,
    get_wind_frecuencia,
)
from pipelines.geografia.queries.tematicas import (
    get_estadistica_detalle,
    get_variables_texto,
)

DETAIL_TOPICS = [
    "geologia",
    "edafologia",
    "pendiente_clasificada",
    "cuencas_clasificac",
    "cuencas_categ",
    "acuiferos_situacion",
    "acuiferos_condicion",
    "clima_koppen",
    "uso_suelo",
    "ndvi",
    "ndwi",
    "anp_humedales_manglares",
    "sequia",
    "erosion_potencial",
    "erosion_efectiva",
    "itur_index_cat",
    "salud_nivel_atencion",
    "educacion_nivel",
    "espacios_publicos",
    "denue_energia",
    "linea_transm_l",
]

TEXT_TOPICS = [
    "geologia",
    "edafologia",
    "pendiente_clasificada",
    "cuencas_clasificac",
    "cuencas_categ",
    "acuiferos_situacion",
    "acuiferos_condicion",
    "clima_koppen",
    "uso_suelo",
    "ndvi",
    "ndwi",
    "anp_humedales_manglares",
    "sequia",
    "erosion_potencial",
    "erosion_efectiva",
    "itur_index_cat",
    "salud_nivel_atencion",
    "educacion_nivel",
    "espacios_publicos",
    "denue_energia",
    "centrales_electricas",
    "predios_centrales_electricas",
    "vientos_dominantes",
]


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        cve_mun = int(input_data)
        cve_mun_3 = f"{cve_mun:03d}"
        cve_geo = f"14{cve_mun_3}"

        ensure_maps()

        settings = DatabaseSettings.from_env("cuadernillos_geo")
        Logger.info("Geografía: conectando a base de datos...")

        with get_session(settings) as session:
            from sqlalchemy import text

            tbl = "cuadernillos_tab.descripcion_general_variables_texto"
            stmt = text(f"SELECT * FROM {tbl} WHERE dg_clave_geo = :cve")
            dg_row = session.execute(stmt, {"cve": int(cve_geo)}).mappings().first()

            if not dg_row:
                raise ValueError(
                    f"Municipality {cve_geo} not found in descripcion_general"
                )

            municipio = dg_row["dg_nombre"]
            Logger.info(f"Geografía: extrayendo datos de {municipio}...")

            texto = {}
            for topic in TEXT_TOPICS:
                try:
                    row = get_variables_texto(session, topic, municipio)
                    if row:
                        texto[topic] = dict(row)
                except Exception:
                    session.rollback()

            detalle = {}
            for topic in DETAIL_TOPICS:
                try:
                    rows = get_estadistica_detalle(session, topic, municipio)
                    detalle[topic] = rows
                except Exception:
                    session.rollback()
                    detalle[topic] = []

            Logger.info("Geografía: extrayendo datos climáticos...")
            temp_long = get_temperatura_long(session, municipio)
            temp_resumen = get_temperatura_resumen(session, municipio)
            prec_long = get_precipitacion_long(session, municipio)
            prec_resumen = get_precipitacion_resumen(session, municipio)
            wind = get_wind_frecuencia(session, cve_mun_3)

        return {
            "cve_mun": cve_mun,
            "cve_geo": cve_geo,
            "municipio": municipio,
            "descripcion_general": dict(dg_row),
            "texto": texto,
            "detalle": detalle,
            "temperatura_long": temp_long,
            "temperatura_resumen": dict(temp_resumen) if temp_resumen else {},
            "precipitacion_long": prec_long,
            "precipitacion_resumen": dict(prec_resumen) if prec_resumen else {},
            "wind": dict(wind) if wind else {},
        }
