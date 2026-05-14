#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from pipeline_common import add_common_args, normalize_clave_geo, setup_logging


def run(municipio: str | None = None, tema: list[str] | None = None, source: str = "local") -> int:
    logger = setup_logging("03_generar_graficas")
    import graficas_core
    if source != "local":
        raise ValueError("La version portable solo acepta source='local'.")
    results_root = settings.DATOS_ESTADISTICOS_DIR

    args = [
        "graficas_core",
        "--results-root",
        str(results_root),
        "--output-root",
        str(settings.GRAFICAS_DIR),
    ]
    for item in tema or []:
        args.extend(["--tema", item])
    if municipio:
        logger.warning(
            "El núcleo de gráficas no filtra por clave municipal; use estadísticas filtradas para %s si requiere salida parcial.",
            normalize_clave_geo(municipio),
        )
    old_argv = sys.argv[:]
    try:
        sys.argv = args
        return graficas_core.main()
    finally:
        sys.argv = old_argv


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera gráficas desde outputs/estadisticas.")
    add_common_args(parser)
    parser.add_argument("--tema", action="append", help="Tema de gráfica a generar. Repetible.")
    parser.add_argument("--source", choices=["local"], default="local", help="Fuente de estadisticas.")
    args = parser.parse_args()
    raise SystemExit(run(municipio=args.municipio, tema=args.tema, source=args.source))


if __name__ == "__main__":
    main()
