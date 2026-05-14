#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from pipeline_common import copy_latest_text_variables, setup_logging


def required_template_vars() -> set[str]:
    text = settings.TEMPLATE_TEX.read_text(encoding="utf-8")
    return set(re.findall(r"<<\s*([A-Za-z_][A-Za-z0-9_]*)\s*>>", text))


def available_text_vars() -> set[str]:
    variables: set[str] = set()
    variables_dir = settings.SALIDAS_DIR / "variables_texto"
    for path in list(settings.DATOS_ESTADISTICOS_DIR.rglob("*_variables_texto.csv")) + list(variables_dir.glob("*.csv")):
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", nrows=1)
        except Exception:
            continue
        variables.update(str(col) for col in df.columns)
    return variables


def is_runtime_var(var: str) -> bool:
    """Variables que render_core calcula aunque no existan como columna CSV."""
    if var.endswith(("_mapa", "_grafica", "_activa", "_activo", "_municipio")):
        return True
    if var.startswith(("pp_", "tm_")) and any(token in var for token in ("_min_", "_max_", "_med_", "_media_")):
        return True
    known = {
        "fecha_documento",
        "municipio",
        "dg_clima_predom",
        "dg_temp_media",
        "dg_prec_acum",
        "dg_geo_predom",
        "dg_edaf_predom",
        "dg_pendiente_predom",
        "dg_grafica_sintesis",
        "dg_viento_grafica",
        "cu_sup_con_disponibilidad",
        "cu_pct_con_disponibilidad",
        "cu_sup_sin_disponibilidad",
        "cu_pct_sin_disponibilidad",
        "cu_sup_reserva",
        "cu_pct_reserva",
        "cu_sup_veda",
        "cu_pct_veda",
        "cu_sup_veda_reglamento",
        "cu_pct_veda_reglamento",
        "cu_sup_veda_reserva_reglamento",
        "cu_pct_veda_reserva_reglamento",
        "cu_sup_sin_ordenamiento_superficial",
        "cu_pct_sin_ordenamiento_superficial",
        "ac_sup_con_disponibilidad",
        "ac_pct_con_disponibilidad",
        "ac_sup_sin_disponibilidad",
        "ac_pct_sin_disponibilidad",
        "ac_sup_sobreexplotado",
        "ac_pct_sobreexplotado",
        "ac_sup_no_sobreexplotado",
        "ac_pct_no_sobreexplotado",
        "salud_total_unidades",
        "ene_conteo_total_municipio",
        "ene_linea_transm_l_km",
        "ene_linea_transm_l_texto",
        "anp_texto_automatico",
    }
    return var in known


def run() -> dict[str, object]:
    logger = setup_logging("02_generar_variables_texto")
    copied = copy_latest_text_variables(logger)
    required = required_template_vars()
    available = available_text_vars()
    missing = sorted(var for var in required - available if not is_runtime_var(var))
    variables_dir = settings.SALIDAS_DIR / "variables_texto"
    variables_dir.mkdir(parents=True, exist_ok=True)
    report = variables_dir / "validacion_variables_latex.csv"
    pd.DataFrame({"variable": missing}).to_csv(report, index=False, encoding="utf-8-sig")
    if missing:
        logger.warning("Variables LaTeX de texto faltantes: %s", ", ".join(missing[:50]))
    logger.info("Reporte de variables: %s", report)
    return {"copied": copied, "missing": missing, "report": str(report)}


def main() -> None:
    argparse.ArgumentParser(description="Consolida variables de texto para LaTeX.").parse_args()
    run()


if __name__ == "__main__":
    main()
