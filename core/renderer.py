import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from core.settings import AppSettings
from core.utils.logger import Logger


def _get_nombre_municipio(municipio_id: str) -> str:
    regions_path = Path("assets/catalogs/regions.json")
    with regions_path.open() as f:
        data = json.load(f)
    for region in data:
        for muns in region.values():
            for m in muns:
                if str(m["id"]) == str(int(municipio_id)):
                    return m["municipio"].replace(" ", "_")
    return municipio_id


def render(municipio_id: str, context: dict) -> Path:
    Logger.info("Renderizando template LaTeX")
    env = Environment(
        loader=FileSystemLoader("templates"),
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<#",
        comment_end_string="#>",
    )
    template = env.get_template("reporte.tex.j2")
    nombre = _get_nombre_municipio(municipio_id)
    slug = f"{municipio_id}_{nombre}_cuadernillo_2026"
    output_path = Path("output/tex") / slug / f"{slug}.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    app_settings = AppSettings()
    output_path.write_text(
        template.render(
            fonts_path=app_settings.FONTS_PATH,
            assets_path=app_settings.ASSETS_PATH,
            **context,
        )
    )
    return output_path
