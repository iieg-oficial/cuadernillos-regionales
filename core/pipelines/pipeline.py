from core.pipelines.section import Section
from core.utils.regions import get_region_by_clave


class Pipeline:
    def __init__(self, sections: list[Section]):
        self.sections = sections

    def run(self, region_clave: str) -> dict:
        region = get_region_by_clave(region_clave)
        nombre = region.nombre
        context = {
            "clave_region": region.clave,
            "nombre_region": nombre[0].lower() + nombre[1:],
        }
        for section in self.sections:
            context |= section.run(region)
        return context
