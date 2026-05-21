from core.db import get_session
from core.pipelines.stage import Stage
from core.settings import DatabaseSettings
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

ANIO_CE = 2024
ANIO_CE_ANTERIOR = 2019


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        cve_mun = int(input_data)

        nombre = None
        ultima_act = None
        unidades_sector_rango = []
        total_estatal_denue = 0
        ranking_denue = None

        try:
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
            pass

        vacb_actual = []
        vacb_anterior = []
        vacb_total_actual = None
        vacb_total_anterior = None

        try:
            ce = DatabaseSettings.from_env("censos_economicos")
            with get_session(ce) as session:
                vacb_actual = get_vacb_por_subsector(session, cve_mun, ANIO_CE)
                vacb_anterior = get_vacb_por_subsector(
                    session, cve_mun, ANIO_CE_ANTERIOR
                )
                vacb_total_actual = get_vacb_total(session, cve_mun, ANIO_CE)
                vacb_total_anterior = get_vacb_total(session, cve_mun, ANIO_CE_ANTERIOR)
        except Exception:
            pass

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
        }
