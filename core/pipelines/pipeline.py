from core.pipelines.section import Section


class Pipeline:
    def __init__(self, sections: list[Section]):
        self.sections = sections

    def run(self, municipio_id: str) -> dict:
        context = {}
        for section in self.sections:
            context |= section.run(municipio_id)
        return context
