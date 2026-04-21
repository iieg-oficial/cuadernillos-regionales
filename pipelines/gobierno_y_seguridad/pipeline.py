from core.pipelines.section import Section
from pipelines.gobierno_y_seguridad.analizer import Analizer
from pipelines.gobierno_y_seguridad.extract import Extract


class GobiernoYSeguridad(Section):
    def run(self, municipio_id: str) -> dict:
        raw = Extract().execute()
        return Analizer(municipio_id).execute(raw)
