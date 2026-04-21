from core.db import get_session
from core.pipelines.stage import Stage
from core.settings import DatabaseSettings
from pipelines.gobierno_y_seguridad.queries.delitos import get_conteo_por_municipio_anio


class Extract(Stage):
    def execute(self, input_data=None) -> list[dict]:
        settings = DatabaseSettings.from_env("fiscalia")
        with get_session(settings) as session:
            return get_conteo_por_municipio_anio(session)
