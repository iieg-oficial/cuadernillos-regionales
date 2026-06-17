from core.db import get_session
from core.pipelines.stage import Stage
from core.settings import DatabaseSettings
from core.utils.logger import Logger
from pipelines.gobierno_y_seguridad.queries.delitos import (
    get_anios_disponibles,
    get_conteo_por_municipio_anio,
)
from pipelines.gobierno_y_seguridad.queries.incidencia import (
    get_carpetas_por_mes,
    get_casos_por_bien_afectado,
    get_casos_por_delito,
    get_ventana_ultimos_meses,
)
from pipelines.gobierno_y_seguridad.queries.ingresos import (
    get_anios_efipem,
    get_ingresos_municipales,
)
from pipelines.gobierno_y_seguridad.queries.participacion import (
    get_participacion_por_municipio,
)
from pipelines.gobierno_y_seguridad.queries.poblacion import (
    get_poblacion_conapo,
)


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        Logger.info("Gobierno y Seguridad: conectando a bases de datos")
        cve_mun = int(input_data)
        cve_municipio = f"14{cve_mun:03d}"

        conteo_municipio_anio = []
        carpetas_por_mes = []
        casos_bien_afectado = []
        casos_por_delito = []
        participacion = []
        anio_actual = 2024
        anio_anterior = 2023

        try:
            Logger.info("Gobierno y Seguridad: extrayendo datos de delitos")
            settings = DatabaseSettings.from_env("delitos_fuero_comun")
            with get_session(settings) as session:
                anios = get_anios_disponibles(session)
                if len(anios) >= 2:
                    anio_actual = anios[0]
                    anio_anterior = anios[1]
                elif anios:
                    anio_actual = anios[0]
                    anio_anterior = anio_actual - 1

                conteo_municipio_anio = get_conteo_por_municipio_anio(
                    session, anio_anterior, anio_actual
                )
                ventana_incidencia = get_ventana_ultimos_meses(session)
                carpetas_por_mes = get_carpetas_por_mes(
                    session, cve_municipio, ventana_incidencia
                )
                casos_bien_afectado = get_casos_por_bien_afectado(
                    session, cve_municipio, ventana_incidencia
                )
                casos_por_delito = get_casos_por_delito(
                    session, cve_municipio, ventana_incidencia
                )
        except Exception:
            Logger.warning(
                "No se pudo conectar a la base de datos de delitos_fuero_comun"
            )

        try:
            Logger.info("Gobierno y Seguridad: extrayendo participación ciudadana")
            settings_pc = DatabaseSettings.from_env("participacion_ciudadana")
            with get_session(settings_pc) as session:
                participacion = get_participacion_por_municipio(session)
        except Exception:
            Logger.warning(
                "No se pudo conectar a la base de datos de participacion_ciudadana"
            )

        ingresos_raw = []
        anio_efipem = None
        anio_anterior_efipem = None
        poblacion = []

        try:
            Logger.info("Gobierno y Seguridad: extrayendo datos de EFIPEM")
            settings_efipem = DatabaseSettings.from_env("efipem")
            with get_session(settings_efipem) as session:
                anios_efipem = get_anios_efipem(session)
                if len(anios_efipem) >= 2:
                    anio_efipem = anios_efipem[0]
                    anio_anterior_efipem = anios_efipem[1]
                elif anios_efipem:
                    anio_efipem = anios_efipem[0]
                    anio_anterior_efipem = anio_efipem - 1

                if anio_efipem:
                    ingresos_raw = get_ingresos_municipales(
                        session, anio_efipem, anio_anterior_efipem
                    )
        except Exception:
            Logger.warning("No se pudo conectar a la base de datos de efipem")

        try:
            Logger.info("Gobierno y Seguridad: extrayendo población CONAPO")
            settings_pob = DatabaseSettings.from_env("conapo")
            with get_session(settings_pob) as session:
                anios_pob = sorted(
                    {
                        a
                        for a in (
                            anio_efipem,
                            anio_anterior_efipem,
                            anio_actual,
                            anio_anterior,
                        )
                        if a
                    }
                )
                poblacion = get_poblacion_conapo(session, anios_pob)
        except Exception:
            Logger.warning("No se pudo conectar a la base de datos de conapo")

        return {
            "anio_actual": anio_actual,
            "anio_anterior": anio_anterior,
            "conteo_municipio_anio": conteo_municipio_anio,
            "carpetas_por_mes": carpetas_por_mes,
            "casos_bien_afectado": casos_bien_afectado,
            "casos_por_delito": casos_por_delito,
            "participacion": participacion,
            "ingresos_raw": ingresos_raw,
            "anio_efipem": anio_efipem,
            "anio_anterior_efipem": anio_anterior_efipem,
            "poblacion": poblacion,
        }
