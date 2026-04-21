from core.pipelines.stage import Stage
from core.utils.municipalities import get_region
from pipelines.gobierno_y_seguridad.helpers.aggregate import aggregate
from pipelines.gobierno_y_seguridad.helpers.ranking import rank
from pipelines.gobierno_y_seguridad.helpers.region import filter_region


class Analizer(Stage):
    def __init__(self, municipio_id: str):
        self.municipio_id = municipio_id

    def execute(self, input_data: list[dict]) -> dict:
        years = sorted({int(r["anio"]) for r in input_data}, reverse=True)
        anio_actual, anio_anterior = years[0], years[1]

        munis = aggregate(input_data, anio_anterior, anio_actual)
        rank(munis)
        region = filter_region(munis, self.municipio_id)

        cvegeo_objetivo = f"14{int(self.municipio_id):03d}"
        nombre = next(
            (m["municipio"] for m in munis if m["cvegeo"] == cvegeo_objetivo),
            self.municipio_id,
        )

        return {
            "gs_municipio_nombre": nombre,
            "gs_region_nombre": get_region(self.municipio_id),
            "gs_anio_anterior": anio_anterior,
            "gs_anio_actual": anio_actual,
            "gs_tabla_delitos": region,
        }
