from core.pipelines.section import Section
from pipelines.directorio_municipal.analizer import Analizer
from pipelines.directorio_municipal.extract import Extract


class DirectorioMunicipal(Section):
    def run(self, municipio_id: str) -> dict:
        raw = Extract().execute(municipio_id)
        return Analizer().execute(raw)
