import re
import tempfile
import unicodedata
import zipfile
from pathlib import Path

import gdown

from core.settings import GeografiaSettings
from core.utils.logger import Logger

MAPS_DIR = Path("assets/maps/geografia")
DRAFT_DIR = Path("output/maps")

MAPA_PLACEHOLDER = (
    "\\includegraphics[width=\\textwidth]{templates/assets/mapa_placeholder.png}"
)

DRAFT_MAX_HEIGHT = 2000
DRAFT_QUALITY = 82

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


def _normalize(text):
    text = unicodedata.normalize("NFKD", str(text).strip().lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def _is_draft():
    settings = GeografiaSettings()
    return settings.GEOGRAFIA_MAPS_QUALITY == "draft"


def _compress_map(src, dest):
    from PIL import Image

    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        if im.height > DRAFT_MAX_HEIGHT:
            ratio = DRAFT_MAX_HEIGHT / im.height
            new_size = (int(im.width * ratio), DRAFT_MAX_HEIGHT)
            im = im.resize(new_size, Image.LANCZOS)
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[3])
            im = bg
        im.save(dest, "JPEG", quality=DRAFT_QUALITY, optimize=True)


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
    Logger.info("Descargando mapas de geografía desde Google Drive...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        Logger.info("Descargando ZIPs desde Drive...")
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


def map_includegraphics(path):
    posix = str(path).replace("\\", "/")
    return f"\\includegraphics[width=0.95\\textwidth]{{\\detokenize{{{posix}}}}}"


def resolve_maps(cve_geo, municipio):
    draft = _is_draft()
    ctx = {}
    for short in TOPIC_FOLDERS:
        path = find_map_for_topic(short, cve_geo, municipio)
        if path:
            if draft:
                path = _get_draft_path(path, cve_geo, short)
            ctx[f"ge_{short}_mapa"] = map_includegraphics(path)
            ctx[f"ge_{short}_mapa_activo"] = True
        else:
            ctx[f"ge_{short}_mapa"] = MAPA_PLACEHOLDER
            ctx[f"ge_{short}_mapa_activo"] = False
    return ctx


def _get_draft_path(original, cve_geo, short):
    draft_path = DRAFT_DIR / cve_geo / f"ge_{short}.jpg"
    if draft_path.exists():
        return draft_path
    _compress_map(original, draft_path)
    return draft_path
