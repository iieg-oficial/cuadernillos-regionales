from core.pipelines.section import Section
from pipelines.demografia.analizer import Analizer
from pipelines.demografia.extract import Extract


class Demografia(Section):
    def run(self, municipio_id: str) -> dict:
        raw = Extract().execute(municipio_id)
        return Analizer(municipio_id).execute(raw)
