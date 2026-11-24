from core.db import get_session
from core.pipelines.stage import Stage
from core.settings import DatabaseSettings
from core.utils.regions import Region
from pipelines.geografia.queries.regional import get_region_indicators


class Extract(Stage):
    def execute(self, input_data: Region):
        settings = DatabaseSettings.from_env("cuadernillos_geo")
        with get_session(settings) as session:
            session.connection(execution_options={"isolation_level": "REPEATABLE READ"})
            return get_region_indicators(session, input_data.clave)
