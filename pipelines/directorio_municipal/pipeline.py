from core.pipelines.section import Section
from core.utils.regions import Region
from pipelines.directorio_municipal.analizer import Analizer
from pipelines.directorio_municipal.extract import Extract


class DirectorioMunicipal(Section):
    def run(self, region: Region) -> dict:
        # Transitorio: municipio representante hasta migrar la sección a la región
        municipio_id = region.representante
        raw = Extract().execute(municipio_id)
        return Analizer().execute(raw)
