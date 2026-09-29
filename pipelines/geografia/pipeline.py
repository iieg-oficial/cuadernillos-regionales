from core.pipelines.section import Section
from core.utils.regions import Region
from pipelines.geografia.analizer import Analizer
from pipelines.geografia.extract import Extract


class Geografia(Section):
    def run(self, region: Region) -> dict:
        # Transitorio: municipio representante hasta migrar la sección a la región
        municipio_id = region.representante
        raw = Extract().execute(municipio_id)
        return Analizer(municipio_id).execute(raw)
