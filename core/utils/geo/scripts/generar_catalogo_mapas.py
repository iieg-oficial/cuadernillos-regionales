#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from catalogo_core import catalogar, municipio_index_from_estadisticas, parsear_variables_template
from config import settings
from pipeline_common import setup_logging


def run() -> str:
    logger = setup_logging("04_generar_catalogo_mapas")
    settings.CATALOGOS_DIR.mkdir(parents=True, exist_ok=True)
    index = municipio_index_from_estadisticas(settings.DATOS_ESTADISTICOS_DIR)
    template_vars = parsear_variables_template(settings.TEMPLATE_TEX)
    catalogo, encontrados, pendientes = catalogar(
        settings.MAPAS_DIR,
        "mapa",
        index,
        template_vars,
        settings.PROJECT_ROOT,
        settings.EXTENSIONES_GRAFICAS,
    )
    out = settings.CATALOGOS_DIR / "catalogo_mapas.csv"
    catalogo.to_csv(out, index=False, encoding="utf-8-sig")
    encontrados.to_csv(settings.CATALOGOS_DIR / "catalogo_mapas_encontrados.csv", index=False, encoding="utf-8-sig")
    pendientes.to_csv(settings.CATALOGOS_DIR / "catalogo_mapas_revision_manual.csv", index=False, encoding="utf-8-sig")
    logger.info("Mapas existentes: %s/%s", int(catalogo["existe"].sum()), len(catalogo))
    return str(out)


def main() -> None:
    argparse.ArgumentParser(description="Genera catálogo de mapas disponibles.").parse_args()
    run()


if __name__ == "__main__":
    main()
