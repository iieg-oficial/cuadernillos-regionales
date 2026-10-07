from core.constants import ND
from core.pipelines.stage import Stage
from core.utils.helpers import latex_escape
from core.utils.logger import Logger


class Analizer(Stage):
    def execute(self, input_data: dict) -> dict:
        Logger.info("Directorio Municipal: procesando datos")
        dm_municipios = []
        for record in input_data["municipios"]:
            dm_municipios.append(
                {
                    "municipio": latex_escape(record["municipio"] or ND),
                    "presidente": latex_escape(record["presidente"] or ND),
                    "correo": latex_escape(record["correo"] or ND),
                    "domicilio": latex_escape(record["domicilio"] or ND),
                    "telefono": latex_escape(record["telefono"] or ND),
                    "sindico": latex_escape(record["sindico"] or ND),
                    "regidores": [
                        latex_escape(regidor) for regidor in record["regidores"]
                    ],
                    "partido": latex_escape(record["partido"] or ND),
                }
            )
        return {"dm_municipios": dm_municipios}
