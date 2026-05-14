#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utilidades compartidas por las etapas editoriales de compilacion."""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings


def setup_logging(name: str) -> logging.Logger:
    settings.ensure_dirs()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    logfile = logging.FileHandler(settings.LOGS_DIR / f"{name}.log", mode="w", encoding="utf-8")
    logfile.setFormatter(fmt)
    logger.addHandler(stream)
    logger.addHandler(logfile)
    return logger


def load_temas_config() -> dict[str, Any]:
    raise RuntimeError("La version portable no usa config/temas_config.json ni calcula estadisticas.")


def filter_config(cfg: dict[str, Any], municipio: str | None = None, tareas: list[str] | None = None) -> dict[str, Any]:
    if tareas:
        allowed = set(tareas)
        for task in cfg.get("tasks", []):
            task["enabled"] = task.get("enabled", True) and (
                task.get("name") in allowed or task.get("out_prefix") in allowed
            )
    cfg["global"]["municipio_filter"] = normalize_clave_geo(municipio) if municipio else None
    return cfg


def normalize_clave_geo(value: object) -> str:
    if value is None:
        return ""
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        return ""
    if len(digits) <= 3:
        return f"14{digits.zfill(3)}"
    return digits.zfill(5)


def copy_latest_text_variables(logger: logging.Logger) -> int:
    variables_dir = settings.SALIDAS_DIR / "variables_texto"
    variables_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in settings.DATOS_ESTADISTICOS_DIR.rglob("*.csv"):
        if path.name.endswith("_variables_texto.csv") or path.name.endswith("_texto_resumen.csv"):
            target = variables_dir / path.name
            shutil.copy2(path, target)
            count += 1
    logger.info("Variables de texto copiadas: %s", count)
    return count


def timed(logger: logging.Logger, label: str, fn, *args, **kwargs):
    start = time.perf_counter()
    logger.info("Inicia: %s", label)
    result = fn(*args, **kwargs)
    logger.info("Termina: %s (%.1f s)", label, time.perf_counter() - start)
    return result


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--municipio", help="Clave municipal de tres digitos o clave_geo de cinco digitos.")
