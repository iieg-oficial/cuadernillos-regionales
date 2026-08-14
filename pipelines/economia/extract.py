import json
from pathlib import Path

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
from pipelines.economia.queries.imss import (
    get_asegurados_municipio,
    get_asegurados_por_division,
    get_asegurados_todos_municipios,
    get_fechas_comparacion,
    get_ultimo_corte,
    sumar_asegurados_estatal,
)
from pipelines.economia.queries.inpc import get_inpc_promedio_anual

ANIO_CE = 2024
ANIO_CE_ANTERIOR = 2019

REGIONS_PATH = Path("assets/catalogs/regions.json")


def _get_nombre_municipio(cve_mun: int) -> str:
    with REGIONS_PATH.open() as f:
        data = json.load(f)
    for region in data:
        for muns in region.values():
            for m in muns:
                if str(m["id"]) == str(cve_mun):
                    return m["municipio"]
    return str(cve_mun)


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        cve_mun = int(input_data)

        Logger.info("Economía: conectando a bases de datos")

        nombre = _get_nombre_municipio(cve_mun)
        ultima_act = None
        unidades_sector_rango = []
        total_estatal_denue = 0
        ranking_denue = None

        try:
            Logger.info("Economía: extrayendo datos del DENUE")
            denue = DatabaseSettings.from_env("denue")
            with get_session(denue) as session:
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

        inpc_promedio_actual = None

        try:
            Logger.info("Economía: extrayendo INPC")
            inpc = DatabaseSettings.from_env("inpc")
            with get_session(inpc) as session:
                inpc_promedio_actual = get_inpc_promedio_anual(session, ANIO_CE - 1)
        except Exception:
            Logger.warning("Economía: no se pudo conectar a INPC")

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

        imss_fecha_corte = None
        imss_asegurados_mun = {}
        imss_asegurados_estatal = 0
        imss_por_division = []
        imss_todos_municipios = []

        try:
            Logger.info("Economía: extrayendo datos del IMSS")
            imss = DatabaseSettings.from_env("asg_imss")
            with get_session(imss) as session:
                imss_fecha_corte = get_ultimo_corte(session)
                if imss_fecha_corte:
                    cvegeo = 14000 + cve_mun
                    t0, t1, t2 = get_fechas_comparacion(imss_fecha_corte)
                    imss_asegurados_mun = get_asegurados_municipio(
                        session, cvegeo, t0, t1, t2
                    )
                    imss_por_division = get_asegurados_por_division(
                        session, cvegeo, t0, t1, t2
                    )
                    imss_todos_municipios = get_asegurados_todos_municipios(
                        session, t0, t1
                    )
                    imss_asegurados_estatal = sumar_asegurados_estatal(
                        imss_todos_municipios
                    )
        except Exception:
            Logger.warning("Economía: no se pudo conectar a IMSS")

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
            "inpc_promedio_actual": inpc_promedio_actual,
            "anio_agricola": anio_agricola,
            "agricola_anual": agricola_anual,
            "agricola_municipal_mdp": agricola_municipal_mdp,
            "agricola_estatal_mdp": agricola_estatal_mdp,
            "anio_ganadero": anio_ganadero,
            "ganadera_anual": ganadera_anual,
            "ganadera_municipal_mdp": ganadera_municipal_mdp,
            "ganadera_estatal_mdp": ganadera_estatal_mdp,
            "imss_fecha_corte": imss_fecha_corte,
            "imss_asegurados_mun": imss_asegurados_mun,
            "imss_asegurados_estatal": imss_asegurados_estatal,
            "imss_por_division": imss_por_division,
            "imss_todos_municipios": imss_todos_municipios,
        }
