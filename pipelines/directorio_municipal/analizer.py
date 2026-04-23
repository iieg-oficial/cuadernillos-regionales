from core.pipelines.stage import Stage

ND = "\\ND"


class Analizer(Stage):
    def execute(self, input_data: dict) -> dict:
        r = input_data

        return {
            "dm_municipio": r.get("municipio") or ND,
            "dm_presidente": r.get("presidente_municipio") or ND,
            "dm_correo": r.get("presidente_correo") or ND,
            "dm_domicilio": r.get("domicilio") or ND,
            "dm_telefono": r.get("directorio_municipal_telefono") or ND,
            "dm_sindico": r.get("directorio_municipal_sindico") or ND,
            "dm_regidores": r.get("directorio_municipal_regidores") or [],
            "dm_partido": r.get("directorio_municipal_partido") or ND,
        }
