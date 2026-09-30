from core.pipelines.section import Section
from core.utils.regions import Region
from pipelines.directorio_municipal.analizer import Analizer
from pipelines.directorio_municipal.extract import Extract


class DirectorioMunicipal(Section):
    def run(self, region: Region) -> dict:
        raw = Extract().execute(region)
        return Analizer().execute(raw)
