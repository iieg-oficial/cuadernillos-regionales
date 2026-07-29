import re
import tempfile
import unicodedata
import zipfile
from pathlib import Path

import gdown

from core.settings import GeografiaSettings
from core.utils.logger import Logger
from core.utils.maps import get_draft_path

MAPS_DIR = Path("assets/maps/geografia")

MAP_BLEED_CM = 0.5

MAPA_PLACEHOLDER = (
    f"\\hspace*{{-{MAP_BLEED_CM}cm}}"
    f"\\includegraphics[width=\\dimexpr\\textwidth + {2 * MAP_BLEED_CM}cm\\relax]"
    "{templates/assets/mapa_placeholder.png}"
)

TOPIC_FOLDERS = {
    "base": "mapa_base",
    "geo": "geologia",
    "ed": "edafologia",
    "tp": "pendientes",
    "cu": "cuencas",
    "ac": "acuiferos",
    "tm": "temperatura",
    "pp": "precipitacion",
    "cl": "clima",
    "usv": "uso_suelo",
    "ndvi": "ndvi",
    "ndwi": "ndwi",
    "anp": "anp",
    "ds": "sequia",
    "er": "erosion_pot",
    "ee": "erosion_efec",
    "itur": "itur",
    "salud": "salud",
    "edu": "educacion",
    "ep": "espacio_pub",
    "ie": "energia",
}

FOLDER_ALIASES = {
    "tp": ["pendientes", "pendiente_clasificada"],
    "tm": ["temperatura", "temperatura_hist"],
    "pp": ["precipitacion", "precipitacion_hist"],
    "cl": ["clima", "clima_koppen"],
    "er": ["erosion_pot", "erosion_potencial"],
    "ee": ["erosion_efec", "erosion_efectiva"],
    "itur": ["itur", "itur_index_cat"],
    "ep": ["espacio_pub", "espacios_publicos"],
    "usv": ["uso_suelo"],
    "base": ["mapa_base"],
}

EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}

DEFAULT_MAP_WIDTH = 1.0


def _normalize(text):
    text = unicodedata.normalize("NFKD", str(text).strip().lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def _is_draft():
    settings = GeografiaSettings()
    return settings.GEOGRAFIA_MAPS_QUALITY == "draft"


def ensure_maps():
    settings = GeografiaSettings()
    url = settings.GEOGRAFIA_MAPS_FOLDER_URL
    if not url:
        return

    missing = [
        name for name in TOPIC_FOLDERS.values() if not _subdir_has_maps(MAPS_DIR / name)
    ]
    if not missing:
        Logger.info("Mapas de geografía: todos presentes")
        return

    Logger.info(
        f"Faltan {len(missing)} carpetas de mapas: "
        f"{', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}"
    )
    Logger.info("Descargando mapas de geografía desde Google Drive")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        Logger.info("Descargando ZIPs desde Drive")
        gdown.download_folder(url, output=str(tmp_path), quiet=True)
        zips = sorted(tmp_path.rglob("*.zip"))
        Logger.info(f"  {len(zips)} archivos ZIP descargados")
        for i, zf in enumerate(zips, 1):
            subdir_name = zf.stem
            dest = MAPS_DIR / subdir_name
            dest.mkdir(parents=True, exist_ok=True)
            count = 0
            with zipfile.ZipFile(zf) as z:
                for member in z.infolist():
                    filename = Path(member.filename).name
                    if not filename:
                        continue
                    ext = Path(filename).suffix.lower()
                    if ext not in EXTENSIONS:
                        continue
                    with z.open(member) as src:
                        (dest / filename).write_bytes(src.read())
                    count += 1
            Logger.info(f"  [{i}/{len(zips)}] {subdir_name}: {count} mapas extraídos")


def _subdir_has_maps(path):
    if not path.is_dir():
        return False
    return len(list(path.glob("*.png"))) >= 125


def _find_map(folder, cve_geo, municipio):
    if not folder.is_dir():
        return None
    norm_mun = _normalize(municipio)
    cve3 = cve_geo[-3:]
    for f in sorted(folder.iterdir()):
        if not f.is_file() or f.suffix.lower() not in EXTENSIONS:
            continue
        stem = _normalize(f.stem)
        tokens = set(stem.split("_"))
        if cve_geo in tokens or stem.endswith(f"_{cve_geo}"):
            return f
        if cve3 in tokens or stem.endswith(f"_{cve3}"):
            return f
        if norm_mun in tokens or stem.endswith(f"_{norm_mun}"):
            return f
    return None


def find_map_for_topic(short, cve_geo, municipio):
    aliases = FOLDER_ALIASES.get(short, [TOPIC_FOLDERS[short]])
    for folder_name in aliases:
        result = _find_map(MAPS_DIR / folder_name, cve_geo, municipio)
        if result:
            return result
    return None


def map_includegraphics(path, width=DEFAULT_MAP_WIDTH):
    posix = str(path).replace("\\", "/")
    img_width = f"\\dimexpr{width}\\textwidth + {2 * MAP_BLEED_CM}cm\\relax"
    return (
        f"\\hspace*{{-{MAP_BLEED_CM}cm}}"
        f"\\includegraphics[width={img_width}]{{\\detokenize{{{posix}}}}}"
    )


def resolve_maps(cve_geo, municipio):
    draft = _is_draft()
    ctx = {}
    for short in TOPIC_FOLDERS:
        path = find_map_for_topic(short, cve_geo, municipio)
        if path:
            if draft:
                path = get_draft_path(path, f"geografia/{cve_geo}", f"ge_{short}")
            ctx[f"ge_{short}_mapa"] = map_includegraphics(path)
            ctx[f"ge_{short}_mapa_activo"] = True
        else:
            ctx[f"ge_{short}_mapa"] = MAPA_PLACEHOLDER
            ctx[f"ge_{short}_mapa_activo"] = False
    return ctx
