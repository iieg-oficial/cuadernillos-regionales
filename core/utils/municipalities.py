import json
from functools import lru_cache
from pathlib import Path

_DATA_PATH = (
    Path(__file__).parent.parent.parent / "assets" / "catalogs" / "regions.json"
)


@lru_cache(maxsize=1)
def _load() -> list[dict]:
    return json.loads(_DATA_PATH.read_text(encoding="utf-8"))


def get_region(municipio_id: str) -> str:
    for entry in _load():
        for region, municipios in entry.items():
            if any(m["id"] == municipio_id for m in municipios):
                return region
    raise ValueError(f"Municipio '{municipio_id}' not found")


def get_municipios_by_region(region: str) -> list[dict]:
    for entry in _load():
        if region in entry:
            return entry[region]
    raise ValueError(f"Region '{region}' not found")


def get_same_region(municipio_id: str) -> list[dict]:
    return get_municipios_by_region(get_region(municipio_id))


def get_same_region_ids(municipio_id: str) -> list[str]:
    return [m["id"] for m in get_same_region(municipio_id)]


def get_all_regions() -> list[str]:
    return [region for entry in _load() for region in entry]


def get_municipio_nombre(municipio_id) -> str:
    clave = int(municipio_id)
    for entry in _load():
        for municipios in entry.values():
            for municipio in municipios:
                if int(municipio["id"]) == clave:
                    return municipio["municipio"]
    raise ValueError(f"Municipio '{municipio_id}' not found")
