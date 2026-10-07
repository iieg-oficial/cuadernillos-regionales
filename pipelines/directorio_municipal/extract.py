import json
import re
import unicodedata
from pathlib import Path

from core.pipelines.stage import Stage
from core.utils.logger import Logger
from core.utils.regions import Region

CATALOG_PATH = Path("assets/catalogs/directorios_municipales.json")


def _normalize(nombre) -> str:
    texto = unicodedata.normalize("NFD", str(nombre))
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def _load_records() -> list[dict]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _record_by_name(records: list[dict], nombre: str) -> dict:
    clave = _normalize(nombre)
    for record in records:
        if _normalize(record["municipio"]) == clave:
            return record
    raise ValueError(f"Municipio '{nombre}' not found in {CATALOG_PATH}")


def _to_dm(record: dict) -> dict:
    return {
        "municipio": record.get("municipio") or "",
        "presidente": record.get("presidente_municipio") or "",
        "correo": record.get("presidente_correo") or "",
        "domicilio": record.get("domicilio") or "",
        "telefono": record.get("directorio_municipal_telefono") or "",
        "sindico": record.get("directorio_municipal_sindico") or "",
        "regidores": list(record.get("directorio_municipal_regidores") or []),
        "partido": record.get("directorio_municipal_partido") or "",
    }


class Extract(Stage):
    def execute(self, region: Region) -> dict:
        Logger.info(f"Directorio Municipal: extrayendo datos de {region.nombre}")
        records = _load_records()
        municipios = [
            _to_dm(_record_by_name(records, m["municipio"])) for m in region.municipios
        ]
        municipios.sort(key=lambda m: m["municipio"])
        return {"municipios": municipios}
