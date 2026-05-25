import json
from pathlib import Path

from core.pipelines.stage import Stage
from core.utils.logger import Logger

CATALOG_PATH = Path("assets/catalogs/directorios_municipales.json")


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        Logger.info("Directorio Municipal: extrayendo datos del catálogo...")
        municipio_id = int(input_data)
        records = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        return next(r for r in records if r["id"] == municipio_id)
