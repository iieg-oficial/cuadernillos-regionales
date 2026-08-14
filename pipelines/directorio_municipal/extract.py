import json
import re
import unicodedata
from pathlib import Path

from core.pipelines.stage import Stage
from core.utils.logger import Logger
from core.utils.municipalities import get_municipio_nombre

CATALOG_PATH = Path("assets/catalogs/directorios_municipales.json")


def _normalize(nombre) -> str:
    texto = unicodedata.normalize("NFD", str(nombre))
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", texto.lower())


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        Logger.info("Directorio Municipal: extrayendo datos del catálogo")
        nombre = get_municipio_nombre(input_data)
        records = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        clave = _normalize(nombre)
        for record in records:
            if _normalize(record["municipio"]) == clave:
                return record
        raise ValueError(f"Municipio '{nombre}' not found in {CATALOG_PATH}")
