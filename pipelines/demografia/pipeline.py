from core.pipelines.section import Section
from core.utils.regions import Region
from pipelines.demografia.analizer import Analizer
from pipelines.demografia.extract import Extract


class Demografia(Section):
    def run(self, region: Region) -> dict:
        # Transitorio: municipio representante hasta migrar la sección a la región
        municipio_id = region.representante
        raw = Extract().execute(municipio_id)
        return Analizer(municipio_id).execute(raw)
