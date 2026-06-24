from core.pipelines.section import Section
from pipelines.economia.analizer import Analizer
from pipelines.economia.extract import Extract


class Economia(Section):
    def run(self, municipio_id: str) -> dict:
        raw = Extract().execute(municipio_id)
        return Analizer(municipio_id).execute(raw)
