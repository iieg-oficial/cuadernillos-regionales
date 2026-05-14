#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Configuracion portable para la compilacion editorial de cuadernillos."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(os.getenv("CUADERNILLOS_ROOT", Path(__file__).resolve().parents[1])).resolve()

CONFIG_DIR = PROJECT_ROOT / "config"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

DATOS_ESTADISTICOS_DIR = Path(os.getenv("CUADERNILLOS_DATOS", PROJECT_ROOT / "datos_estadisticos")).resolve()
MAPAS_DIR = Path(os.getenv("CUADERNILLOS_MAPAS", PROJECT_ROOT / "mapas")).resolve()
GRAFICAS_DIR = Path(os.getenv("CUADERNILLOS_GRAFICAS", PROJECT_ROOT / "graficas")).resolve()
CATALOGOS_DIR = Path(os.getenv("CUADERNILLOS_CATALOGOS", PROJECT_ROOT / "catalogos")).resolve()
LATEX_DIR = PROJECT_ROOT / "latex"
TEMPLATES_DIR = LATEX_DIR / "templates"
ASSETS_DIR = LATEX_DIR / "assets"
SALIDAS_DIR = PROJECT_ROOT / "salidas"
TEX_DIR = SALIDAS_DIR / "tex"
PDF_DIR = SALIDAS_DIR / "pdf"
LOGS_DIR = PROJECT_ROOT / "logs"

TEMPLATE_TEX = Path(os.getenv("CUADERNILLOS_TEMPLATE", TEMPLATES_DIR / "main.tex")).resolve()
HEADER_IMAGE = Path(os.getenv("CUADERNILLOS_LOGO_HEADER", ASSETS_DIR / "logo_header.png")).resolve()
FOOTER_IMAGE = Path(os.getenv("CUADERNILLOS_LOGO_FOOTER", ASSETS_DIR / "logo_footer.png")).resolve()
COVER_IMAGE = Path(os.getenv("CUADERNILLOS_PORTADA", ASSETS_DIR / "portada.png")).resolve()
PLACEHOLDER_IMAGE = Path(os.getenv("CUADERNILLOS_PLACEHOLDER", ASSETS_DIR / "placeholder.png")).resolve()

EXTENSIONES_GRAFICAS = {".png", ".jpg", ".jpeg", ".pdf"}


def ensure_dirs() -> None:
    for path in [
        DATOS_ESTADISTICOS_DIR,
        MAPAS_DIR,
        GRAFICAS_DIR,
        CATALOGOS_DIR,
        TEMPLATES_DIR,
        ASSETS_DIR,
        TEX_DIR,
        PDF_DIR,
        LOGS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
