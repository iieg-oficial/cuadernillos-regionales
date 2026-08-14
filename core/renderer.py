import json
import unicodedata
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from core.settings import AppSettings
from core.utils.escudos import ensure_escudos, escudo_path
from core.utils.logger import Logger

PROD_TEX_DIR = Path("output/tex/prod")


def _sin_acentos(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def _get_nombre_municipio(municipio_id: str) -> str:
    regions_path = Path("assets/catalogs/regions.json")
    with regions_path.open() as f:
        data = json.load(f)
    for region in data:
        for muns in region.values():
            for m in muns:
                if str(m["id"]) == str(int(municipio_id)):
                    return _sin_acentos(m["municipio"]).lower().replace(" ", "_")
    return municipio_id


def render(municipio_id: str, context: dict, prod: bool = False) -> Path:
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
    slug = f"{municipio_id}_{nombre}_cuadernillo_municipal_2026"
    if prod:
        output_path = PROD_TEX_DIR / f"{slug}.tex"
    else:
        output_path = Path("output/tex") / slug / f"{slug}.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    app_settings = AppSettings()
    ensure_escudos()
    escudo = escudo_path(municipio_id)
    output_path.write_text(
        template.render(
            fonts_path=app_settings.FONTS_PATH,
            assets_path=app_settings.ASSETS_PATH,
            escudo_path=str(escudo) if escudo else None,
            **context,
        )
    )
    return output_path
