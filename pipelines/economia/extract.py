from core.db import get_session
from core.pipelines.stage import Stage
from core.settings import DatabaseSettings
from core.utils.logger import Logger
from pipelines.economia.queries.agropecuario import (
    get_ultimo_anio_agricola,
    get_valor_produccion_agricola_anual,
    get_valor_produccion_agricola_estatal,
    get_valor_produccion_agricola_municipal,
)
from pipelines.economia.queries.censos_economicos import (
    get_vacb_por_subsector,
    get_vacb_total,
)
from pipelines.economia.queries.denue import (
    get_nombre_municipio,
    get_ranking_y_total_estatal,
    get_ultima_actualizacion,
    get_unidades_por_sector_y_rango,
)
from pipelines.economia.queries.ganaderia import (
    get_ultimo_anio_ganadero,
    get_valor_produccion_ganadera_anual,
    get_valor_produccion_ganadera_estatal,
    get_valor_produccion_ganadera_municipal,
)

ANIO_CE = 2024
ANIO_CE_ANTERIOR = 2019


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        cve_mun = int(input_data)

        Logger.info("Economía: conectando a bases de datos")

        nombre = None
        ultima_act = None
        unidades_sector_rango = []
        total_estatal_denue = 0
        ranking_denue = None

        try:
            Logger.info("Economía: extrayendo datos del DENUE")
            denue = DatabaseSettings.from_env("denue")
            with get_session(denue) as session:
                nombre = get_nombre_municipio(session, cve_mun)
                act_row = get_ultima_actualizacion(session)
                if act_row:
                    ultima_act = act_row.fecha_actualizacion
                    act_id = act_row.id
                    unidades_sector_rango = get_unidades_por_sector_y_rango(
                        session, cve_mun, act_id
                    )
                    total_estatal_denue, ranking_denue = get_ranking_y_total_estatal(
                        session, cve_mun, act_id
                    )
        except Exception:
            Logger.warning("Economía: no se pudo conectar a DENUE")

        vacb_actual = []
        vacb_anterior = []
        vacb_total_actual = None
        vacb_total_anterior = None

        try:
            Logger.info("Economía: extrayendo censos económicos")
            ce = DatabaseSettings.from_env("censos_economicos")
            with get_session(ce) as session:
                vacb_actual = get_vacb_por_subsector(session, cve_mun, ANIO_CE)
                vacb_anterior = get_vacb_por_subsector(
                    session, cve_mun, ANIO_CE_ANTERIOR
                )
                vacb_total_actual = get_vacb_total(session, cve_mun, ANIO_CE)
                vacb_total_anterior = get_vacb_total(session, cve_mun, ANIO_CE_ANTERIOR)
        except Exception:
            Logger.warning("Economía: no se pudo conectar a censos económicos")

        agricola_anual = []
        agricola_municipal_mdp = None
        agricola_estatal_mdp = None
        anio_agricola = None

        try:
            Logger.info("Economía: extrayendo datos agropecuarios")
            siap = DatabaseSettings.from_env("agropecuario_siap")
            with get_session(siap) as session:
                anio_agricola = get_ultimo_anio_agricola(session)
                if anio_agricola:
                    agricola_anual = get_valor_produccion_agricola_anual(
                        session, cve_mun
                    )
                    agricola_municipal_mdp = get_valor_produccion_agricola_municipal(
                        session, cve_mun, anio_agricola
                    )
                    agricola_estatal_mdp = get_valor_produccion_agricola_estatal(
                        session, anio_agricola
                    )
        except Exception:
            Logger.warning("Economía: no se pudo conectar a agropecuario SIAP")

        ganadera_anual = []
        ganadera_municipal_mdp = None
        ganadera_estatal_mdp = None
        anio_ganadero = None

        try:
            Logger.info("Economía: extrayendo datos ganaderos")
            gan = DatabaseSettings.from_env("produccion_ganadera")
            with get_session(gan) as session:
                anio_ganadero = get_ultimo_anio_ganadero(session)
                if anio_ganadero:
                    ganadera_anual = get_valor_produccion_ganadera_anual(
                        session, cve_mun
                    )
                    ganadera_municipal_mdp = get_valor_produccion_ganadera_municipal(
                        session, cve_mun, anio_ganadero
                    )
                    ganadera_estatal_mdp = get_valor_produccion_ganadera_estatal(
                        session, anio_ganadero
                    )
        except Exception:
            Logger.warning("Economía: no se pudo conectar a producción ganadera")

        return {
            "cve_mun": cve_mun,
            "municipio_nombre": nombre,
            "ultima_actualizacion_denue": ultima_act,
            "unidades_sector_rango": unidades_sector_rango,
            "total_estatal_denue": total_estatal_denue,
            "ranking_denue": ranking_denue,
            "anio_ce": ANIO_CE,
            "anio_ce_anterior": ANIO_CE_ANTERIOR,
            "vacb_actual": vacb_actual,
            "vacb_anterior": vacb_anterior,
            "vacb_total_actual": vacb_total_actual,
            "vacb_total_anterior": vacb_total_anterior,
            "anio_agricola": anio_agricola,
            "agricola_anual": agricola_anual,
            "agricola_municipal_mdp": agricola_municipal_mdp,
            "agricola_estatal_mdp": agricola_estatal_mdp,
            "anio_ganadero": anio_ganadero,
            "ganadera_anual": ganadera_anual,
            "ganadera_municipal_mdp": ganadera_municipal_mdp,
            "ganadera_estatal_mdp": ganadera_estatal_mdp,
        }
