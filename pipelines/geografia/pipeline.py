from core.pipelines.section import Section
from pipelines.geografia.analizer import Analizer
from pipelines.geografia.extract import Extract


class Geografia(Section):
    def run(self, municipio_id: str) -> dict:
        raw = Extract().execute(municipio_id)
        return Analizer(municipio_id).execute(raw)
