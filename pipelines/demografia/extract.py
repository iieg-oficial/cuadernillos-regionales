from core.db import get_session
from core.pipelines.stage import Stage
from core.settings import DatabaseSettings
from pipelines.demografia.queries.marginacion import (
    get_marginacion_estatal,
    get_marginacion_jalisco,
    get_marginacion_localidades,
)
from pipelines.demografia.queries.migracion import get_iim_estados, get_iim_municipios
from pipelines.demografia.queries.poblacion import (
    get_localidades_por_anio,
    get_nombre_municipio,
    get_total_estatal,
    get_totales_municipio,
)
from pipelines.demografia.queries.pobreza import (
    get_pobreza_jalisco,
    get_pobreza_municipio,
    get_pobreza_por_entidad,
)


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        cve_mun = int(input_data)

        pob = DatabaseSettings.from_env("censo_poblacion")
        iim = DatabaseSettings.from_env("intensidad_migratoria")
        marg = DatabaseSettings.from_env("marginacion")
        pob_multi = DatabaseSettings.from_env("pobreza_multidimensional")

        with get_session(pob) as session:
            nombre = get_nombre_municipio(session, cve_mun)
            totales = get_totales_municipio(session, cve_mun)
            localidades_2020 = get_localidades_por_anio(session, cve_mun, 2020)
            localidades_2010 = get_localidades_por_anio(session, cve_mun, 2010)
            total_estatal_2020 = get_total_estatal(session, 2020)

        with get_session(iim) as session:
            iim_mun_2020 = get_iim_municipios(session, 2020)
            iim_mun_2010 = get_iim_municipios(session, 2010)
            iim_estados_2020 = get_iim_estados(session, 2020)

        with get_session(marg) as session:
            marginacion_2020 = get_marginacion_jalisco(session, 2020)
            marginacion_2015 = get_marginacion_jalisco(session, 2015)
            marginacion_2010 = get_marginacion_jalisco(session, 2010)
            marginacion_localidades = get_marginacion_localidades(
                session, cve_mun, 2020
            )
            marginacion_estatal_2020 = get_marginacion_estatal(session, 14, 2020)

        cve_mun_str = f"14{cve_mun:03d}"
        with get_session(pob_multi) as session:
            pobreza_2020 = get_pobreza_municipio(session, cve_mun_str, 2020)
            pobreza_2015 = get_pobreza_municipio(session, cve_mun_str, 2015)
            pobreza_jalisco_2020 = get_pobreza_jalisco(session, 2020)
            pobreza_por_entidad_2020 = get_pobreza_por_entidad(session, 2020)

        return {
            "municipio_nombre": nombre,
            "totales_poblacion": totales,
            "localidades_2020": localidades_2020,
            "localidades_2010": localidades_2010,
            "total_estatal_2020": total_estatal_2020,
            "iim_municipios_2020": iim_mun_2020,
            "iim_municipios_2010": iim_mun_2010,
            "iim_estados_2020": iim_estados_2020,
            "marginacion_jalisco_2020": marginacion_2020,
            "marginacion_jalisco_2015": marginacion_2015,
            "marginacion_jalisco_2010": marginacion_2010,
            "marginacion_localidades": marginacion_localidades,
            "marginacion_estatal_2020": marginacion_estatal_2020,
            "pobreza_2020": pobreza_2020,
            "pobreza_2015": pobreza_2015,
            "pobreza_jalisco_2020": pobreza_jalisco_2020,
            "pobreza_por_entidad_2020": pobreza_por_entidad_2020,
        }
