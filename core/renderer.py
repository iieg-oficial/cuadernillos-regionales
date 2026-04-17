from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from core.settings import AppSettings


def render(municipio_id: str, context: dict) -> Path:
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
    slug = f"{municipio_id}_cuadernillo"
    output_path = Path("output/tex") / slug / f"{slug}.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    app_settings = AppSettings()
    output_path.write_text(
        template.render(fonts_path=app_settings.FONTS_PATH, **context)
    )
    return output_path
