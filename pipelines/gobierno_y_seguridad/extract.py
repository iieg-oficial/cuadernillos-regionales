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
)
from pipelines.gobierno_y_seguridad.queries.participacion import (
    get_participacion_por_municipio,
)


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
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
                carpetas_por_mes = get_carpetas_por_mes(
                    session, cve_municipio, anio_anterior, anio_actual
                )
                casos_bien_afectado = get_casos_por_bien_afectado(
                    session, cve_municipio, anio_anterior, anio_actual
                )

                if casos_bien_afectado:
                    principal_bien = casos_bien_afectado[0]["bien_afectado"]
                    casos_por_delito = get_casos_por_delito(
                        session,
                        cve_municipio,
                        principal_bien,
                        anio_anterior,
                        anio_actual,
                    )
        except Exception:
            Logger.warning(
                "No se pudo conectar a la base de datos de delitos_fuero_comun"
            )

        try:
            settings_pc = DatabaseSettings.from_env("participacion_ciudadana")
            with get_session(settings_pc) as session:
                participacion = get_participacion_por_municipio(session)
        except Exception:
            Logger.warning(
                "No se pudo conectar a la base de datos de participacion_ciudadana"
            )

        return {
            "anio_actual": anio_actual,
            "anio_anterior": anio_anterior,
            "conteo_municipio_anio": conteo_municipio_anio,
            "carpetas_por_mes": carpetas_por_mes,
            "casos_bien_afectado": casos_bien_afectado,
            "casos_por_delito": casos_por_delito,
            "participacion": participacion,
        }
