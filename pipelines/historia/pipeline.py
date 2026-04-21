from core.pipelines.section import Section
from pipelines.historia.analizer import Analizer
from pipelines.historia.extract import Extract


class Historia(Section):
    def run(self, municipio_id: str) -> dict:
        raw = Extract().execute(municipio_id)
        return Analizer(municipio_id).execute(raw)
