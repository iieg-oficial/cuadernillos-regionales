from core.pipelines.section import Section
from core.utils.regions import Region
from pipelines.geografia.analizer import Analizer
from pipelines.geografia.extract import Extract


class Geografia(Section):
    def run(self, region: Region) -> dict:
        return Analizer(region.clave).execute(Extract().execute(region))
