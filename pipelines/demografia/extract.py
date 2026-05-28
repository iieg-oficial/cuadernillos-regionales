import tempfile
import zipfile
from pathlib import Path

import gdown

from core.db import get_session
from core.pipelines.stage import Stage
from core.settings import DatabaseSettings, DemografiaSettings
from core.utils.logger import Logger
from core.utils.maps import get_draft_path
from core.utils.municipalities import get_region, get_same_region_ids
from pipelines.demografia.queries.marginacion import (
    get_marginacion_estatal,
    get_marginacion_jalisco,
    get_marginacion_localidades,
)
from pipelines.demografia.queries.migracion import get_iim_estados, get_iim_jalisco
from pipelines.demografia.queries.poblacion import (
    get_localidades_por_anio,
    get_nombre_municipio,
    get_total_estatal,
    get_total_region,
    get_totales_municipio,
)
from pipelines.demografia.queries.pobreza import (
    get_pobreza_jalisco,
    get_pobreza_municipio,
    get_pobreza_por_entidad,
)

MAPS_DIR = Path("assets/maps/demografia")


def _ensure_maps() -> None:
    settings = DemografiaSettings()
    for subdir, url in (
        ("migracion", settings.DEMOGRAFIA_MAPS_MIGRACION_URL),
        ("pobreza", settings.DEMOGRAFIA_MAPS_POBREZA_URL),
        ("marginacion", settings.DEMOGRAFIA_MAPS_MARGINACION_URL),
    ):
        dest = MAPS_DIR / subdir
        if not url or (dest.exists() and len(list(dest.glob("*.png"))) >= 125):
            continue
        dest.mkdir(parents=True, exist_ok=True)
        Logger.info(f"Descargando mapas de {subdir} desde Google Drive")
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / f"{subdir}.zip"
            gdown.download(url=url, output=str(zip_path), quiet=True)
            with zipfile.ZipFile(zip_path) as zf:
                for member in zf.infolist():
                    filename = Path(member.filename).name
                    if not filename or not filename.endswith(".png"):
                        continue
                    with zf.open(member) as src, (dest / filename).open("wb") as dst:
                        dst.write(src.read())
        n = len(list(dest.iterdir()))
        Logger.info(f"Mapas de {subdir} descargados ({n} archivos)")


def _find_map(subdir: str, municipio_id: int) -> Path | None:
    cvegeo = f"14{municipio_id:03d}"
    p = MAPS_DIR / subdir / f"{subdir}_{cvegeo}.png"
    if not p.exists():
        return None
    settings = DemografiaSettings()
    if settings.DEMOGRAFIA_MAPS_QUALITY == "draft":
        return get_draft_path(p, f"demografia/{cvegeo}", f"de_{subdir}")
    return p


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        cve_mun = int(input_data)

        _ensure_maps()

        Logger.info("Demografía: conectando a bases de datos")
        pob = DatabaseSettings.from_env("censo_poblacion")
        iim = DatabaseSettings.from_env("intensidad_migratoria")
        marg = DatabaseSettings.from_env("marginacion")
        pob_multi = DatabaseSettings.from_env("pobreza_multidimensional")

        region_name = get_region(str(cve_mun))
        region_ids = [int(mid) for mid in get_same_region_ids(str(cve_mun))]

        Logger.info("Demografía: extrayendo datos de población")
        with get_session(pob) as session:
            nombre = get_nombre_municipio(session, cve_mun)
            totales = get_totales_municipio(session, cve_mun)
            localidades_2020 = get_localidades_por_anio(session, cve_mun, 2020)
            localidades_2010 = get_localidades_por_anio(session, cve_mun, 2010)
            total_estatal_2020 = get_total_estatal(session, 2020)
            total_region_2020 = get_total_region(session, region_ids, 2020)

        Logger.info("Demografía: extrayendo datos de migración")
        with get_session(iim) as session:
            iim_mun_2020 = get_iim_jalisco(session, 2020)
            iim_mun_2010 = get_iim_jalisco(session, 2010)
            iim_estados_2020 = get_iim_estados(session, 2020)

        Logger.info("Demografía: extrayendo datos de marginación")
        with get_session(marg) as session:
            marginacion_2020 = get_marginacion_jalisco(session, 2020)
            marginacion_2015 = get_marginacion_jalisco(session, 2015)
            marginacion_2010 = get_marginacion_jalisco(session, 2010)
            marginacion_localidades = get_marginacion_localidades(
                session, cve_mun, 2020
            )
            marginacion_estatal_2020 = get_marginacion_estatal(session, 14, 2020)

        Logger.info("Demografía: extrayendo datos de pobreza")
        cve_mun_str = f"14{cve_mun:03d}"
        with get_session(pob_multi) as session:
            pobreza_2020 = get_pobreza_municipio(session, cve_mun_str, 2020)
            pobreza_2015 = get_pobreza_municipio(session, cve_mun_str, 2015)
            pobreza_jalisco_2020 = get_pobreza_jalisco(session, 2020)
            pobreza_por_entidad_2020 = get_pobreza_por_entidad(session, 2020)

        return {
            "municipio_nombre": nombre,
            "region_nombre": region_name,
            "totales_poblacion": totales,
            "total_region_2020": total_region_2020,
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
            "mapa_migracion": _find_map("migracion", cve_mun),
            "mapa_pobreza": _find_map("pobreza", cve_mun),
            "mapa_marginacion": _find_map("marginacion", cve_mun),
        }
