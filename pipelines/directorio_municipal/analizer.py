from core.constants import ND
from core.pipelines.stage import Stage
from core.utils.helpers import latex_escape
from core.utils.logger import Logger


class Analizer(Stage):
    def execute(self, input_data: dict) -> dict:
        Logger.info("Directorio Municipal: procesando datos")
        r = input_data

        return {
            "dm_municipio": latex_escape(r.get("municipio") or ND),
            "dm_presidente": latex_escape(r.get("presidente_municipio") or ND),
            "dm_correo": latex_escape(r.get("presidente_correo") or ND),
            "dm_domicilio": latex_escape(r.get("domicilio") or ND),
            "dm_telefono": latex_escape(r.get("directorio_municipal_telefono") or ND),
            "dm_sindico": latex_escape(r.get("directorio_municipal_sindico") or ND),
            "dm_regidores": [
                latex_escape(x) for x in (r.get("directorio_municipal_regidores") or [])
            ],
            "dm_partido": latex_escape(r.get("directorio_municipal_partido") or ND),
        }
