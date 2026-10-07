import json
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_DATA_PATH = (
    Path(__file__).parent.parent.parent / "assets" / "catalogs" / "regiones.json"
)

TOTAL_REGIONES = 12


@dataclass(frozen=True)
class Region:
    clave: str
    nombre: str
    representante: str
    municipios: list[dict]


@lru_cache(maxsize=1)
def _load() -> list[dict]:
    return json.loads(_DATA_PATH.read_text(encoding="utf-8"))


def normalize_clave(clave: str) -> str:
    try:
        numero = int(clave)
    except (TypeError, ValueError):
        raise ValueError(f"Clave de región '{clave}' inválida") from None
    if not 1 <= numero <= TOTAL_REGIONES:
        raise ValueError(f"Clave de región '{clave}' fuera de rango")
    return f"{numero:02d}"


def _regiones() -> list[Region]:
    return [
        Region(
            clave=entry["clave"],
            nombre=entry["region"],
            representante=entry["representante"],
            municipios=entry["municipios"],
        )
        for entry in sorted(_load(), key=lambda e: e["clave"])
    ]


def get_all_regions() -> list[Region]:
    return _regiones()


def get_all_region_claves() -> list[str]:
    return [region.clave for region in _regiones()]


def get_region_by_clave(clave: str) -> Region:
    normalizada = normalize_clave(clave)
    for region in _regiones():
        if region.clave == normalizada:
            return region
    raise ValueError(f"Región '{clave}' not found")


def get_region_nombre(clave: str) -> str:
    return get_region_by_clave(clave).nombre


def get_municipio_ids(clave: str) -> list[str]:
    return [m["id"] for m in get_region_by_clave(clave).municipios]


def get_representante(clave: str) -> str:
    return get_region_by_clave(clave).representante


def _sin_acentos(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def get_region_slug(clave: str) -> str:
    region = get_region_by_clave(clave)
    nombre = _sin_acentos(region.nombre).lower().replace(" ", "_")
    return f"{region.clave}_{nombre}"
