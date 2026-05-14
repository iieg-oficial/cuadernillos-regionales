#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import importlib
import logging
import sys
import time
from pathlib import Path

from config import settings


ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def setup_logger() -> logging.Logger:
    settings.ensure_dirs()
    logger = logging.getLogger("run_compilacion")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    file_handler = logging.FileHandler(settings.LOGS_DIR / "run_compilacion.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(stream)
    logger.addHandler(file_handler)
    return logger


def require_inputs() -> None:
    missing = []
    if not any(settings.DATOS_ESTADISTICOS_DIR.rglob("*.csv")):
        missing.append(f"estadisticas CSV en {settings.DATOS_ESTADISTICOS_DIR}")
    if not settings.TEMPLATE_TEX.exists():
        missing.append(f"plantilla LaTeX en {settings.TEMPLATE_TEX}")
    if missing:
        raise FileNotFoundError("Faltan entradas requeridas: " + "; ".join(missing))


def run_stage(logger: logging.Logger, label: str, module_name: str, **kwargs):
    logger.info("Inicia: %s", label)
    start = time.perf_counter()
    module = importlib.import_module(module_name)
    result = module.run(**kwargs)
    logger.info("Termina: %s (%.1f s)", label, time.perf_counter() - start)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Compila cuadernillos desde estadisticas y mapas ya exportados.")
    parser.add_argument("--municipio", help="Clave municipal de tres digitos o clave_geo de cinco digitos.")
    parser.add_argument("--tema", action="append", help="Tema de grafica a generar. Repetible.")
    parser.add_argument("--skip-graficas", action="store_true")
    parser.add_argument("--skip-variables", action="store_true")
    parser.add_argument("--skip-catalogos", action="store_true")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--compile", action="store_true", help="Compila PDF con latexmk/xelatex.")
    parser.add_argument("--tex-only", action="store_true", help="Solo renderiza .tex.")
    parser.add_argument("--limit", type=int, help="Limita municipios para pruebas controladas.")
    args = parser.parse_args()

    logger = setup_logger()
    try:
        require_inputs()
        if not args.skip_graficas:
            run_stage(logger, "generacion de graficas", "generar_graficas", municipio=args.municipio, tema=args.tema)
        if not args.skip_variables:
            run_stage(logger, "generacion de variables de texto", "generar_variables_texto")
        if not args.skip_catalogos:
            run_stage(logger, "catalogo de mapas", "generar_catalogo_mapas")
            run_stage(logger, "catalogo de graficas", "generar_catalogo_graficas")
        if not args.skip_render:
            run_stage(
                logger,
                "render LaTeX/PDF",
                "render_latex",
                municipio=args.municipio,
                compile_pdf=args.compile,
                tex_only=args.tex_only or not args.compile,
                limit=args.limit,
            )
    except Exception:
        logger.exception("El flujo de compilacion fallo.")
        return 1
    logger.info("Flujo de compilacion terminado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
