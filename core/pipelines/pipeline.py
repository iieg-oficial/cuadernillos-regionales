from core.pipelines.section import Section
from core.utils.regions import get_region_by_clave


class Pipeline:
    def __init__(self, sections: list[Section]):
        self.sections = sections

    def run(self, region_clave: str) -> dict:
        region = get_region_by_clave(region_clave)
        context = {
            "clave_region": region.clave,
            "nombre_region": region.nombre,
        }
        for section in self.sections:
            context |= section.run(region)
        return context
