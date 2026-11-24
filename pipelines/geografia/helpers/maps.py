from pathlib import Path

from core.settings import GeografiaSettings
from core.utils.maps import get_draft_path
from core.utils.regions import get_region_nombre

MAPS_DIR = Path("assets/maps/geografia/regiones")
MAPA_PLACEHOLDER = r"\mapageo{templates/assets/mapa_placeholder.png}"

TOPIC_FILES = {
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

EXTENSIONS = (".png", ".jpg", ".jpeg", ".pdf")


def resolve_maps(clave):
    draft = GeografiaSettings().GEOGRAFIA_MAPS_QUALITY == "draft"
    nombre = get_region_nombre(clave)
    context = {}
    for short, topic in TOPIC_FILES.items():
        stem = MAPS_DIR / topic / f"{topic}_{nombre}"
        path = next(
            (
                stem.with_suffix(ext)
                for ext in EXTENSIONS
                if stem.with_suffix(ext).is_file()
            ),
            None,
        )
        if path and draft and path.suffix != ".pdf":
            path = get_draft_path(path, f"geografia/regiones/{clave}", f"ge_{short}")
        context[f"ge_{short}_mapa_activo"] = path is not None
        context[f"ge_{short}_mapa"] = (
            rf"\mapageo{{\detokenize{{{path.as_posix()}}}}}"
            if path
            else MAPA_PLACEHOLDER
        )
    return context
