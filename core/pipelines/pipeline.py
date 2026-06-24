from core.pipelines.section import Section
from core.utils.municipalities import get_region


class Pipeline:
    def __init__(self, sections: list[Section]):
        self.sections = sections

    def run(self, municipio_id: str) -> dict:
        region = get_region(municipio_id)
        context = {"nombre_region": region[0].lower() + region[1:]}
        for section in self.sections:
            context |= section.run(municipio_id)
        return context
