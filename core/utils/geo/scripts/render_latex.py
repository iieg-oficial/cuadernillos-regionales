#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from pipeline_common import add_common_args, normalize_clave_geo, setup_logging


def configure_render_core(results_root=None):
    import render_core

    render_core.ROOT = settings.PROJECT_ROOT
    render_core.RESULTS = results_root or settings.DATOS_ESTADISTICOS_DIR
    render_core.TEMPLATE_DIR = settings.TEMPLATES_DIR
    render_core.TEMPLATE_NAME = settings.TEMPLATE_TEX.name
    render_core.OUT_DIR = settings.SALIDAS_DIR
    render_core.CATALOGOS_LATEX = settings.CATALOGOS_DIR
    render_core.CATALOGO_MAPAS = settings.CATALOGOS_DIR / "catalogo_mapas.csv"
    render_core.CATALOGO_GRAFICAS = settings.CATALOGOS_DIR / "catalogo_graficas.csv"
    render_core.HEADER_IMAGE = settings.HEADER_IMAGE
    render_core.FOOTER_IMAGE = settings.FOOTER_IMAGE
    render_core.COVER_IMAGE = settings.COVER_IMAGE
    render_core.PLACEHOLDER_SOURCE_IMAGE = settings.PLACEHOLDER_IMAGE
    return render_core


def install_municipio_filter(render_core, municipio: str | None) -> None:
    clave = normalize_clave_geo(municipio)
    if not clave:
        return
    original = render_core.build_contexts

    def filtered_contexts():
        contexts = original()
        return [ctx for ctx in contexts if normalize_clave_geo(ctx.get("dg_clave_geo")) == clave]

    render_core.build_contexts = filtered_contexts


def run(
    municipio: str | None = None,
    compile_pdf: bool = False,
    tex_only: bool = False,
    limit: int | None = None,
    source: str = "local",
) -> dict:
    logger = setup_logging("06_render_latex")
    if source != "local":
        raise ValueError("La version portable solo acepta source='local'.")
    results_root = settings.DATOS_ESTADISTICOS_DIR

    render_core = configure_render_core(results_root=results_root)
    install_municipio_filter(render_core, municipio)
    result = render_core.render(limit=limit, compile_pdf=compile_pdf, keep_tex_only=tex_only)

    logger.info("Renderizados: %s", result["rendered"])
    logger.info("Errores de compilación: %s", len(result["compile_errors"]))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Renderiza cuadernillos LaTeX desde variables, mapas y gráficas.")
    add_common_args(parser)
    parser.add_argument("--compile", action="store_true", help="Compila PDF con latexmk/xelatex.")
    parser.add_argument("--tex-only", action="store_true", help="Sólo genera .tex.")
    parser.add_argument("--limit", type=int, help="Límite de municipios para prueba.")
    parser.add_argument("--source", choices=["local"], default="local", help="Fuente de estadisticas.")
    args = parser.parse_args()
    run(municipio=args.municipio, compile_pdf=args.compile, tex_only=args.tex_only, limit=args.limit, source=args.source)


if __name__ == "__main__":
    main()
