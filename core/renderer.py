from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from core.settings import AppSettings
from core.utils.escudos import ensure_escudos, escudo_path
from core.utils.logger import Logger
from core.utils.regions import get_region_by_clave, get_region_slug

PROD_TEX_DIR = Path("output/tex/prod")
BUNDLE_FONTS_DIR = "fonts"


def render(clave_region: str, context: dict, prod: bool = False) -> Path:
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
    region = get_region_by_clave(clave_region)
    slug = f"{get_region_slug(region.clave)}_cuadernillo_regional_2026"
    if prod:
        output_path = PROD_TEX_DIR / slug / f"{slug}.tex"
    else:
        output_path = Path("output/tex") / slug / f"{slug}.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    app_settings = AppSettings()
    ensure_escudos()
    escudo = escudo_path(region.representante)
    output_path.write_text(
        template.render(
            fonts_path=f"{BUNDLE_FONTS_DIR}/" if prod else app_settings.FONTS_PATH,
            assets_path=app_settings.ASSETS_PATH,
            escudo_path=str(escudo) if escudo else None,
            **context,
        )
    )
    return output_path
