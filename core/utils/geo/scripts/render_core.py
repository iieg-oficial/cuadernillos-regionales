#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import binascii
import csv
from decimal import Decimal, InvalidOperation
import math
import os
import re
import shutil
import sqlite3
import struct
import subprocess
import unicodedata
import zlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd
from jinja2 import Environment, FileSystemLoader


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "datos_estadisticos"
TEMPLATE_DIR = ROOT / "latex" / "templates"
TEMPLATE_NAME = "main.tex"
OUT_DIR = ROOT / "salidas"
CATALOGOS_LATEX = ROOT / "catalogos"
CATALOGO_MAPAS = CATALOGOS_LATEX / "catalogo_mapas.csv"
CATALOGO_GRAFICAS = CATALOGOS_LATEX / "catalogo_graficas.csv"
HEADER_IMAGE = ROOT / "latex" / "assets" / "logo_header.png"
FOOTER_IMAGE = ROOT / "latex" / "assets" / "logo_footer.png"
COVER_IMAGE = ROOT / "latex" / "assets" / "portada.png"
PLACEHOLDER_SOURCE_IMAGE = ROOT / "latex" / "assets" / "placeholder.png"
WIND_GRAPH_DIRS = [
    ROOT / "graficas" / "vientos_dominantes",
    ROOT / "mapas" / "vientos_dominantes",
]

MONTHS = {
    "ENE": ("ene", "Enero"),
    "FEB": ("feb", "Febrero"),
    "MAR": ("mar", "Marzo"),
    "ABR": ("abr", "Abril"),
    "MAY": ("may", "Mayo"),
    "JUN": ("jun", "Junio"),
    "JUL": ("jul", "Julio"),
    "AGO": ("ago", "Agosto"),
    "SEP": ("sep", "Septiembre"),
    "OCT": ("oct", "Octubre"),
    "NOV": ("nov", "Noviembre"),
    "DIC": ("dic", "Diciembre"),
    "ANUAL": ("anual", "Anual"),
}

PLACEHOLDER_PNG = b""


def slugify(text: str) -> str:
    replacements = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    text = text.translate(replacements).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "sin_nombre"


def compact_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(text)).strip("_")


def image_name_candidates(prefixes: Iterable[str], municipio: str) -> List[str]:
    raw = str(municipio).strip()
    slug = slugify(raw)
    compact = compact_name(raw)
    variants = [raw, raw.replace(" ", "_"), compact, compact.lower(), slug]
    seen = set()
    names = []
    for prefix in prefixes:
        for variant in variants:
            for ext in (".png", ".jpg", ".jpeg", ".pdf"):
                name = f"{prefix}_{variant}{ext}"
                if name not in seen:
                    seen.add(name)
                    names.append(name)
    return names


def find_municipal_image(search_dirs: Iterable[Path], prefixes: Iterable[str], municipio: str) -> Optional[Path]:
    for directory in search_dirs:
        for name in image_name_candidates(prefixes, municipio):
            candidate = directory / name
            if candidate.exists():
                return candidate
    return None


def render_asset_path(source: Optional[Path], subdir: str, basename: str) -> str:
    if source is None:
        return "placeholder.png"
    asset_dir = OUT_DIR / "assets" / subdir
    asset_dir.mkdir(parents=True, exist_ok=True)
    destination = asset_dir / f"{basename}{source.suffix.lower()}"
    shutil.copyfile(source, destination)
    return destination.relative_to(OUT_DIR).as_posix()


def first_context_value(ctx: Dict[str, Any], *keys: str, default: Any = "ND") -> Any:
    for key in keys:
        value = ctx.get(key)
        if value is None:
            continue
        if isinstance(value, float) and math.isnan(value):
            continue
        if pd.isna(value):
            continue
        text = str(value).strip()
        if text and text.upper() != "ND":
            return value
    return default


def strip_percent_symbol(value: Any) -> Any:
    if value is None:
        return value
    if isinstance(value, float) and math.isnan(value):
        return value
    if pd.isna(value):
        return value
    text = str(value).strip()
    return re.sub(r"\s*\\?%\s*$", "", text).strip()


def latex_escape(value: Any) -> str:
    if value is None:
        return "ND"
    if isinstance(value, float) and math.isnan(value):
        return "ND"
    if pd.isna(value):
        return "ND"
    if isinstance(value, float):
        value = f"{value:.2f}".rstrip("0").rstrip(".")
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


DISPLAY_NUMBER_RE = re.compile(r"^\s*(-?\d+)(\.\d+)?\s*$")
RAW_FIELD_TOKENS = ("lat", "lon", "coord", "coordenada", "clave", "cve", "id")
RAW_FIELD_NAMES = {"class_value", "categoria"}


def format_number_es(value: Any) -> Any:
    if value is None:
        return value
    if isinstance(value, float) and math.isnan(value):
        return value
    if pd.isna(value):
        return value

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        text = str(value)
    elif isinstance(value, str):
        text = value.strip()
    else:
        return value

    match = DISPLAY_NUMBER_RE.match(text)
    if not match:
        return value

    try:
        number = Decimal(match.group(1) + (match.group(2) or ""))
    except InvalidOperation:
        return value

    sign = "-" if number < 0 else ""
    plain = format(abs(number), "f")
    integer, dot, decimals = plain.partition(".")
    integer = f"{int(integer):,}".replace(",", " ")
    decimals = decimals.rstrip("0")
    return f"{sign}{integer}{dot}{decimals}" if decimals else f"{sign}{integer}"


def fmt(value: Any, field_name: Optional[str] = None) -> str:
    normalized = value
    field = (field_name or "").lower()
    if field and field not in RAW_FIELD_NAMES and not any(token in field for token in RAW_FIELD_TOKENS):
        normalized = format_number_es(value)
    return latex_escape(normalized)


def sentence_case_words(value: Any) -> Any:
    if value is None:
        return value
    if isinstance(value, float) and math.isnan(value):
        return value
    if pd.isna(value):
        return value
    text = str(value).strip()
    if not text:
        return text
    text = re.sub(r"\s+", " ", text.lower())
    return text[:1].upper() + text[1:]


def to_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if pd.isna(value):
        return None
    text = str(value).strip().replace(",", "").replace("%", "")
    if not text or text.upper() == "ND":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def is_positive(value: Any) -> bool:
    number = to_number(value)
    return number is not None and number > 0


def dominant_category(df: pd.DataFrame, municipio: str, category_col: str = "categoria") -> Any:
    work = df[df["municipio"] == municipio].copy()
    if work.empty or category_col not in work.columns:
        return "ND"
    if "orden_pct" in work.columns:
        work["orden_pct"] = pd.to_numeric(work["orden_pct"], errors="coerce")
        work = work.sort_values("orden_pct", na_position="last")
    elif "porcentaje" in work.columns:
        work["porcentaje"] = pd.to_numeric(work["porcentaje"], errors="coerce")
        work = work.sort_values("porcentaje", ascending=False, na_position="last")
    return work.iloc[0].get(category_col, "ND")


def build_anp_text(ctx: Dict[str, Any]) -> str:
    municipio = fmt(first_context_value(ctx, "anp_nombre", "dg_nombre", "municipio"), field_name="municipio")
    has_anp = is_positive(ctx.get("anp_num_anp")) or is_positive(ctx.get("anp_superficie_anp"))
    has_humedales = is_positive(ctx.get("anp_pct_humedales"))

    if has_anp:
        count = fmt(ctx.get("anp_num_anp"), field_name="anp_num_anp")
        superficie = fmt(ctx.get("anp_superficie_anp"), field_name="anp_superficie_anp")
        pct = fmt(strip_percent_symbol(ctx.get("anp_pct_anp")), field_name="anp_pct_anp")
        area_word = "área natural protegida" if to_number(ctx.get("anp_num_anp")) == 1 else "áreas naturales protegidas"
        parts = [
            f"El municipio de {municipio} registra {count} {area_word}, con una superficie de {superficie} hectáreas, equivalente a {pct} \\% del territorio municipal."
        ]
    else:
        parts = ["El municipio no registra áreas naturales protegidas dentro de su territorio."]

    if has_humedales:
        pct_humedales = fmt(strip_percent_symbol(ctx.get("anp_pct_humedales")), field_name="anp_pct_humedales")
        prefix = "Asimismo, " if has_anp else ""
        parts.append(f"{prefix}Los humedales abarcan {pct_humedales} \\% del territorio municipal.")
    elif not has_anp:
        parts = ["El municipio no registra áreas naturales protegidas ni humedales dentro de su territorio."]

    return " ".join(parts).rstrip(".")


def municipal_value(df: pd.DataFrame, municipio: str, column: str) -> Any:
    if column not in df.columns:
        return None
    work = df[df["municipio"] == municipio]
    if work.empty:
        return None
    return work.iloc[0].get(column)


def build_linea_transmision_text(value: Any) -> str:
    number = to_number(value)
    if number is None:
        return "No se dispone de información sobre la longitud de redes de alta tensión para el municipio."
    if number <= 0:
        return "No existen redes de alta tensión registradas."
    return f"Existen {fmt(value, field_name='longitud_km_total_municipio')} kilómetros lineales de redes de alta tensión."


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def normalize_clave_geo(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if not digits:
        return ""
    if len(digits) <= 3:
        return f"14{digits.zfill(3)}"
    return digits.zfill(5)


def truthy_catalog_value(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "si", "sí"}


def latex_graphic_path(path_value: Any) -> str:
    path = str(path_value or "").strip()
    if not path:
        return ""
    return r"\detokenize{" + path.replace("\\", "/") + "}"


def load_catalog_assets() -> Dict[str, Dict[str, str]]:
    """
    Rutas graficas catalogadas para inyectar en el contexto Jinja.
    Si los catalogos no existen, el render conserva placeholders.
    """
    assets: Dict[str, Dict[str, str]] = {}
    for path in (CATALOGO_MAPAS, CATALOGO_GRAFICAS):
        if not path.exists():
            continue
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
        required = {"clave_geo", "variable_tex", "path_relativo", "existe"}
        if not required.issubset(df.columns):
            continue
        for _, row in df.iterrows():
            if not truthy_catalog_value(row.get("existe")):
                continue
            variable = str(row.get("variable_tex", "")).strip()
            asset_path = str(row.get("path_absoluto", "")).strip() or str(row.get("path_relativo", "")).strip()
            clave = normalize_clave_geo(row.get("clave_geo"))
            if not clave or not variable or not asset_path:
                continue
            assets.setdefault(clave, {})[variable] = latex_graphic_path(asset_path)
    return assets


def normalize_key(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "nombre" in df.columns:
        df = df.rename(columns={"nombre": "municipio"})
    if "municipio" not in df.columns and "dg_nombre" in df.columns:
        df["municipio"] = df["dg_nombre"]
    if "clave_geo" not in df.columns and "dg_clave_geo" in df.columns:
        df["clave_geo"] = df["dg_clave_geo"]
    return df


def load_municipios() -> pd.DataFrame:
    path = RESULTS / "descripcion_general" / "descripcion_general_variables_texto.csv"
    if path.exists():
        df = normalize_key(read_csv(path))
    else:
        candidates = sorted(RESULTS.rglob("*_variables_texto.csv"))
        if not candidates:
            raise RuntimeError(f"No se encontraron variables de texto en {RESULTS}")
        df = normalize_key(read_csv(candidates[0]))
    if "dg_nombre" in df.columns and "municipio" not in df.columns:
        df["municipio"] = df["dg_nombre"]
    if "dg_clave_geo" in df.columns and "clave_geo" not in df.columns:
        df["clave_geo"] = df["dg_clave_geo"]
    required = {"clave_geo", "municipio"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Faltan campos municipales en estadisticas: {missing}")
    cols = [col for col in ["clave_geo", "municipio", "region", "area_km2", "area_ha"] if col in df.columns]
    df = df[cols].drop_duplicates("clave_geo").sort_values("municipio")
    return df


def load_text_tables() -> pd.DataFrame:
    selected: Dict[str, Path] = {}
    for path in RESULTS.rglob("*.csv"):
        if not (path.name.endswith("_variables_texto.csv") or path.name.endswith("_texto_resumen.csv")):
            continue
        current = selected.get(path.name)
        if current is None or path.stat().st_mtime > current.stat().st_mtime:
            selected[path.name] = path

    frames: List[pd.DataFrame] = []
    for path in sorted(selected.values()):
        df = normalize_key(read_csv(path))
        if "municipio" in df.columns:
            frames.append(df)

    if not frames:
        raise RuntimeError(f"No se encontraron tablas narrativas en {RESULTS}")

    merged = frames[0]
    for df in frames[1:]:
        overlap = [c for c in df.columns if c in merged.columns and c != "municipio"]
        if overlap:
            df = df.drop(columns=overlap)
        merged = merged.merge(df, on="municipio", how="outer")
    return merged


def load_detail_tables() -> Dict[str, pd.DataFrame]:
    """
    Tablas del cuerpo del cuadernillo: solo archivos *_detalle.csv.
    Actualmente las salidas se llaman *_estadistica_detalle.csv, por lo que
    entran en este criterio sin depender de resúmenes ni coberturas.
    """
    selected: Dict[str, Path] = {}
    for path in RESULTS.rglob("*_detalle.csv"):
        key = path.name.removesuffix("_estadistica_detalle.csv").removesuffix("_detalle.csv")
        current = selected.get(key)
        if current is None or path.stat().st_mtime > current.stat().st_mtime:
            selected[key] = path

    tables: Dict[str, pd.DataFrame] = {}
    for key, path in sorted(selected.items()):
        tables[key] = normalize_key(read_csv(path))
    if not tables:
        raise RuntimeError(f"No se encontraron tablas *_detalle.csv en {RESULTS}")
    return tables


def required_detail(tables: Dict[str, pd.DataFrame], key: str) -> pd.DataFrame:
    if key not in tables:
        available = ", ".join(sorted(tables))
        raise KeyError(f"Falta tabla de detalle '{key}'. Disponibles: {available}")
    return tables[key]


def csv_from_results(path: str) -> pd.DataFrame:
    return normalize_key(read_csv(RESULTS / path))


def rows_for(
    df: pd.DataFrame,
    municipio: str,
    columns: Dict[str, str],
    order_col: str = "orden_pct",
    transforms: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    work = df[df["municipio"] == municipio].copy()
    if order_col in work.columns:
        work[order_col] = pd.to_numeric(work[order_col], errors="coerce")
        work = work.sort_values(order_col, na_position="last")
    rows = []
    transforms = transforms or {}
    for _, row in work.iterrows():
        current = {}
        for out, src in columns.items():
            value = row.get(src)
            transform = transforms.get(src)
            if transform is not None:
                value = transform(value)
            current[out] = fmt(value, field_name=src)
        rows.append(current)
    return rows


def _sort_text_key(value: Any) -> str:
    text = "" if pd.isna(value) else str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def health_level_label(value: Any) -> Any:
    text = sentence_case_words(value)
    if _sort_text_key(text) == "no aplica":
        return "Otros"
    return text


def health_level_order(value: Any) -> int:
    key = _sort_text_key(value)
    if "primer" in key:
        return 1
    if "segundo" in key:
        return 2
    if "tercer" in key:
        return 3
    if key == "no aplica":
        return 4
    return 999


def health_rows_for(df: pd.DataFrame, municipio: str) -> List[Dict[str, str]]:
    work = df[df["municipio"] == municipio].copy()
    if work.empty:
        return []

    work["_orden_nivel_salud"] = work["nivel_de_atencion"].map(health_level_order)
    work["_orden_institucion_salud"] = work["nombre_de_la_institucion"].map(_sort_text_key)
    work = work.sort_values(
        ["_orden_nivel_salud", "_orden_institucion_salud"],
        na_position="last",
    )

    rows = []
    for _, row in work.iterrows():
        rows.append({
            "nombre_de_la_institucion": fmt(row.get("nombre_de_la_institucion"), field_name="nombre_de_la_institucion"),
            "nivel_atencion": fmt(health_level_label(row.get("nivel_de_atencion")), field_name="nivel_de_atencion"),
            "cantidad": fmt(row.get("conteo"), field_name="conteo"),
        })
    return rows


def education_rows_for(df: pd.DataFrame, municipio: str) -> List[Dict[str, str]]:
    level_order = {
        "Inicial": 1,
        "Preescolar": 2,
        "Primaria": 3,
        "Secundaria": 4,
        "Bachillerato": 5,
        "Licenciatura": 6,
        "Profesional Tecnico": 7,
        "Técnico": 7,
    }
    level_labels = {
        "Profesional Tecnico": "Técnico",
    }
    sector_order = {"Público": 1, "Particular": 2}

    work = df[df["municipio"] == municipio].copy()
    if work.empty:
        return []

    work["nivel"] = work["nivel"].astype(str).str.strip()
    work["sostenimiento_reclasificado"] = work["sostenimiento_reclasificado"].astype(str).str.strip()
    work["_orden_nivel"] = work["nivel"].map(level_order).fillna(999)
    work["_orden_sector"] = work["sostenimiento_reclasificado"].map(sector_order).fillna(999)
    work = work.sort_values(["_orden_nivel", "nivel", "_orden_sector", "sostenimiento_reclasificado"])

    rows = []
    for _, row in work.iterrows():
        nivel = level_labels.get(row.get("nivel"), row.get("nivel"))
        rows.append({
            "nivel_educativo": fmt(nivel, field_name="nivel"),
            "sector": fmt(row.get("sostenimiento_reclasificado"), field_name="sostenimiento_reclasificado"),
            "cantidad": fmt(row.get("conteo"), field_name="conteo"),
        })
    return rows


def pct_sum(df: pd.DataFrame, municipio: str, contains: Iterable[str], value_col: str = "porcentaje") -> str:
    work = df[df["municipio"] == municipio].copy()
    if "categoria" not in work.columns or value_col not in work.columns:
        return "ND"
    terms = [t.lower() for t in contains]
    mask = work["categoria"].fillna("").astype(str).str.lower().apply(lambda x: any(t in x for t in terms))
    return fmt(pd.to_numeric(work.loc[mask, value_col], errors="coerce").sum(), field_name=value_col)


def sup_sum(df: pd.DataFrame, municipio: str, contains: Iterable[str], value_col: str = "superficie_ha") -> str:
    work = df[df["municipio"] == municipio].copy()
    if "categoria" not in work.columns or value_col not in work.columns:
        return "ND"
    terms = [t.lower() for t in contains]
    mask = work["categoria"].fillna("").astype(str).str.lower().apply(lambda x: any(t in x for t in terms))
    return fmt(pd.to_numeric(work.loc[mask, value_col], errors="coerce").sum(), field_name=value_col)


def climate_context(long_df: pd.DataFrame, municipio: str, prefix: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    work = long_df[long_df["municipio"] == municipio].copy()
    for periodo, (short, _label) in MONTHS.items():
        row = work[work["periodo"] == periodo]
        if row.empty:
            continue
        item = row.iloc[0]
        out[f"{prefix}_min_{short}"] = fmt(item.get("min"), field_name="min")
        out[f"{prefix}_max_{short}"] = fmt(item.get("max"), field_name="max")
        out[f"{prefix}_med_{short}"] = fmt(item.get("mean"), field_name="mean")
        if prefix == "pp":
            out[f"{prefix}_media_{short}"] = fmt(item.get("mean"), field_name="mean")
    return out


def copy_or_placeholder(source: Path, destination: Path, placeholder: bytes) -> None:
    if source.exists():
        shutil.copyfile(source, destination)
        return
    destination.write_bytes(placeholder)


def write_placeholder_assets(out_dir: Path) -> str:
    img = out_dir / "placeholder.png"
    if PLACEHOLDER_SOURCE_IMAGE.exists():
        shutil.copyfile(PLACEHOLDER_SOURCE_IMAGE, img)
    else:
        img.write_bytes(make_placeholder_png())
    copy_or_placeholder(HEADER_IMAGE, out_dir / "logo_header.png", img.read_bytes())
    copy_or_placeholder(FOOTER_IMAGE, out_dir / "logo_footer.png", img.read_bytes())
    copy_or_placeholder(COVER_IMAGE, out_dir / "portada.png", img.read_bytes())
    return "placeholder.png"


def make_placeholder_png(width: int = 1200, height: int = 800) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        crc = binascii.crc32(kind + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)

    # RGB PNG sin alpha, con fondo gris claro. Cada fila inicia con filtro 0.
    row = b"\x00" + (b"\xF2\xF2\xF2" * width)
    raw = row * height
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, level=9))
        + chunk(b"IEND", b"")
    )


def all_template_variables(template_text: str) -> List[str]:
    found = re.findall(r"<<\s*([A-Za-z_][A-Za-z0-9_]*)\s*>>", template_text)
    return sorted(set(found))


def build_contexts() -> List[Dict[str, Any]]:
    municipios = load_municipios()
    text = load_text_tables()
    base = municipios.merge(text, on="municipio", how="left")
    if "clave_geo" not in base.columns:
        for candidate in ("clave_geo_x", "clave_geo_y", "dg_clave_geo"):
            if candidate in base.columns:
                base["clave_geo"] = base[candidate]
                break
    detail_tables = load_detail_tables()
    catalog_assets = load_catalog_assets()

    details = {
        "geo": required_detail(detail_tables, "geologia"),
        "ed": required_detail(detail_tables, "edafologia"),
        "tp": required_detail(detail_tables, "pendiente_clasificada"),
        "cu": required_detail(detail_tables, "cuencas_clasificac"),
        "cu_categ": required_detail(detail_tables, "cuencas_categ"),
        "ac_sit": required_detail(detail_tables, "acuiferos_situacion"),
        "ac_cond": required_detail(detail_tables, "acuiferos_condicion"),
        "cl": required_detail(detail_tables, "clima_koppen"),
        "usv": required_detail(detail_tables, "uso_suelo"),
        "ndvi": required_detail(detail_tables, "ndvi"),
        "ndwi": required_detail(detail_tables, "ndwi"),
        "anp": required_detail(detail_tables, "anp_humedales_manglares"),
        "ds": required_detail(detail_tables, "sequia"),
        "er": required_detail(detail_tables, "erosion_potencial"),
        "ee": required_detail(detail_tables, "erosion_efectiva"),
        "itur": required_detail(detail_tables, "itur_index_cat"),
        "salud": required_detail(detail_tables, "salud_nivel_atencion"),
        "edu": required_detail(detail_tables, "educacion_nivel"),
        "ep": required_detail(detail_tables, "espacios_publicos"),
        "ie": required_detail(detail_tables, "denue_energia"),
        "linea_transm_l": required_detail(detail_tables, "linea_transm_l"),
    }
    # Excepción necesaria: temperatura y precipitación no generan *_detalle.csv;
    # sus tablas mensuales del template salen de *_long.csv.
    temp_long = csv_from_results("temperatura_hist/temperatura_hist_long.csv")
    prec_long = csv_from_results("precipitacion_hist/precipitacion_hist_long.csv")

    contexts: List[Dict[str, Any]] = []
    for _, row in base.iterrows():
        municipio = row["municipio"]
        ctx = {col: fmt(row.get(col), field_name=col) for col in base.columns}
        ctx["municipio"] = fmt(municipio, field_name="municipio")
        ctx["fecha_documento"] = "Abril 2026"

        ctx.update({
            "dg_nombre": ctx.get("dg_nombre", fmt(municipio, field_name="municipio")),
            "dg_clave_geo": ctx.get("dg_clave_geo", fmt(row.get("clave_geo"), field_name="clave_geo")),
            "dg_region": ctx.get("dg_region", fmt(row.get("region"), field_name="region")),
            "dg_area_km2": ctx.get("dg_area_km2", fmt(row.get("area_km2"), field_name="area_km2")),
            "dg_area_ha": ctx.get("dg_area_ha", fmt(row.get("area_ha"), field_name="area_ha")),
            "dg_clima_predom": ctx.get("cl_tipo_predominante", "ND"),
            "dg_temp_media": ctx.get("tm_media_anual", ctx.get("t_media_anual", "ND")),
            "dg_prec_acum": ctx.get("p_acumulada_anual", "ND"),
            "dg_geo_predom": fmt(first_context_value(
                ctx,
                "geo_dominante",
                default=dominant_category(details["geo"], municipio),
            ), field_name="geo_dominante"),
            "dg_edaf_predom": ctx.get("ed_dominante", "ND"),
            "dg_pendiente_predom": ctx.get("tp_dominante", "ND"),
            "dg_nombre_cabecera": ctx.get("dg_nombre_cabecera", "ND"),
            "dg_lat": ctx.get("dg_lat", "ND"),
            "dg_lon": ctx.get("dg_lon", "ND"),
            "dg_elev1": ctx.get("dg_elev1", "ND"),
            "dg_elevmin": ctx.get("dg_elevmin", "ND"),
            "dg_elevmax": ctx.get("dg_elevmax", "ND"),
            "dg_colindantes": ctx.get("dg_colindantes", "ND"),
            "dg_viento_predom": fmt(first_context_value(
                ctx,
                "dg_viento_predom",
                "viento_predom",
                "viento_dominante",
                "vd_direccion_predominante",
                "direccion_viento_predominante",
            ), field_name="dg_viento_predom"),
            "dg_viento_predom_fr": fmt(strip_percent_symbol(first_context_value(
                row,
                "dg_viento_predom_fr",
                "viento_predom_fr",
                "viento_dominante_fr",
                "vd_frecuencia_anual",
                "frecuencia_viento_predominante",
            )), field_name="dg_viento_predom_fr"),
        })

        ctx.update({
            "dg_municipio": ctx["dg_nombre"],
            "dg_sup_mun_km2": ctx["dg_area_km2"],
            "dg_nom_cabecera": ctx["dg_nombre_cabecera"],
            "dg_cabecera_lat": ctx["dg_lat"],
            "dg_cabecera_lon": ctx["dg_lon"],
            "dg_cabecera_alt": ctx["dg_elev1"],
            "dg_altitud_min": ctx["dg_elevmin"],
            "dg_altitud_max": ctx["dg_elevmax"],
            "dg_mun_colindantes": ctx["dg_colindantes"],
        })

        for short in [
            "base", "geo", "ed", "tp", "cu", "ac", "tm", "pp", "cl", "usv", "ndvi", "ndwi",
            "anp", "ds", "er", "ee", "itur", "salud", "edu", "ep", "ie",
        ]:
            ctx[f"{short}_mapa"] = "placeholder.png"
            ctx[f"{short}_grafica"] = "placeholder.png"
            ctx[f"{short}_mapa_activo"] = False
            ctx[f"{short}_grafica_activa"] = False
            ctx[f"{short}_municipio"] = fmt(municipio, field_name="municipio")
        ctx["dg_grafica_sintesis"] = "placeholder.png"
        ctx["dg_viento_grafica_activa"] = False
        wind_graph = find_municipal_image(
            WIND_GRAPH_DIRS,
            ["vientos_dominantes", "viento_dominante", "rosa_vientos", "windrose", "wind_rose"],
            municipio,
        )
        ctx["dg_viento_grafica"] = render_asset_path(
            wind_graph,
            "vientos_dominantes",
            f"vientos_dominantes_{slugify(str(municipio))}",
        )
        if wind_graph is not None:
            ctx["dg_viento_grafica_activa"] = True
        for variable, rel_path in catalog_assets.get(normalize_clave_geo(row.get("clave_geo")), {}).items():
            ctx[variable] = rel_path
            if variable.endswith("_grafica"):
                ctx[f"{variable}_activa"] = True
            if variable.endswith("_mapa"):
                ctx[f"{variable}_activo"] = True

        ctx.update(climate_context(temp_long, municipio, "tm"))
        ctx.update(climate_context(prec_long, municipio, "pp"))

        ctx.update({
            "geo_unidades_geologicas": rows_for(details["geo"], municipio, {"roca": "categoria", "superficie_ha": "superficie_ha", "porcentaje": "porcentaje"}),
            "ed_tipos_suelo": rows_for(details["ed"], municipio, {"tipo_suelo": "categoria", "superficie_ha": "superficie_ha", "porcentaje": "porcentaje"}),
            "tp_pendientes": rows_for(details["tp"], municipio, {"categoria": "categoria", "superficie_ha": "superficie_ha_aj", "porcentaje": "porcentaje"}, order_col="orden_clase"),
            "cl_clasificaciones": rows_for(details["cl"], municipio, {"clasificacion_climatica": "categoria", "superficie_ha": "superficie_ha", "porcentaje": "porcentaje"}),
            "usv_clasificacion": rows_for(details["usv"], municipio, {"grupo": "categoria", "superficie_ha": "superficie_ha", "porcentaje": "porcentaje"}),
            "ndvi_categorias": rows_for(details["ndvi"], municipio, {"categoria": "categoria", "superficie_ha_aj": "superficie_ha_aj", "porcentaje": "porcentaje"}, order_col="orden_clase"),
            "ndwi_categorias": rows_for(details["ndwi"], municipio, {"categoria": "categoria", "superficie_ha_aj": "superficie_ha_aj", "porcentaje": "porcentaje"}, order_col="orden_clase"),
            "anp_categorias": rows_for(details["anp"], municipio, {"categoria": "categoria", "superficie_ha": "superficie_ha", "porcentaje": "porcentaje", "descripcion": "cadena_texto"}),
            "ds_categorias": rows_for(details["ds"], municipio, {"categoria": "categoria", "superficie_ha": "superficie_ha_aj", "porcentaje": "porcentaje"}, order_col="orden_clase"),
            "er_categorias": rows_for(details["er"], municipio, {"categoria": "rango_texto", "superficie_ha": "superficie_ha_aj", "porcentaje": "porcentaje"}, order_col="orden_clase"),
            "ee_categorias": rows_for(details["ee"], municipio, {"categoria": "rango_texto", "superficie_ha": "superficie_ha_aj", "porcentaje": "porcentaje"}, order_col="orden_clase"),
            "itur_clasificaciones": rows_for(details["itur"], municipio, {"categoria": "categoria", "superficie_ha": "superficie_ha", "porcentaje": "porcentaje"}),
            "salud_unidades": health_rows_for(details["salud"], municipio),
            "edu_centros": education_rows_for(details["edu"], municipio),
            "ep_espacios": rows_for(details["ep"], municipio, {"tipo": "categoria", "superficie_ha": "conteo", "porcentaje": "porcentaje"}),
            "ie_infraestructura": rows_for(details["ie"], municipio, {"tipo_infraestructura": "categoria", "valor": "conteo", "porcentaje": "porcentaje"}),
        })

        ctx.update({
            "cu_sup_con_disponibilidad": sup_sum(details["cu"], municipio, ["con disponibilidad"]),
            "cu_pct_con_disponibilidad": pct_sum(details["cu"], municipio, ["con disponibilidad"]),
            "cu_sup_sin_disponibilidad": sup_sum(details["cu"], municipio, ["sin disponibilidad"]),
            "cu_pct_sin_disponibilidad": pct_sum(details["cu"], municipio, ["sin disponibilidad"]),
            "cu_sup_reserva": sup_sum(details["cu_categ"], municipio, ["reserva"]),
            "cu_pct_reserva": pct_sum(details["cu_categ"], municipio, ["reserva"]),
            "cu_sup_veda": sup_sum(details["cu_categ"], municipio, ["veda"]),
            "cu_pct_veda": pct_sum(details["cu_categ"], municipio, ["veda"]),
            "cu_sup_veda_reglamento": sup_sum(details["cu_categ"], municipio, ["veda y reglamento"]),
            "cu_pct_veda_reglamento": pct_sum(details["cu_categ"], municipio, ["veda y reglamento"]),
            "cu_sup_veda_reserva_reglamento": sup_sum(details["cu_categ"], municipio, ["veda, reserva y reglamento"]),
            "cu_pct_veda_reserva_reglamento": pct_sum(details["cu_categ"], municipio, ["veda, reserva y reglamento"]),
            "cu_sup_sin_ordenamiento_superficial": sup_sum(details["cu_categ"], municipio, ["sin ordenamiento"]),
            "cu_pct_sin_ordenamiento_superficial": pct_sum(details["cu_categ"], municipio, ["sin ordenamiento"]),
            "ac_sup_con_disponibilidad": sup_sum(details["ac_sit"], municipio, ["con disponibilidad"]),
            "ac_pct_con_disponibilidad": pct_sum(details["ac_sit"], municipio, ["con disponibilidad"]),
            "ac_sup_sin_disponibilidad": sup_sum(details["ac_sit"], municipio, ["sin disponibilidad"]),
            "ac_pct_sin_disponibilidad": pct_sum(details["ac_sit"], municipio, ["sin disponibilidad"]),
            "ac_sup_sobreexplotado": sup_sum(details["ac_cond"], municipio, ["sobreexplotado"]),
            "ac_pct_sobreexplotado": pct_sum(details["ac_cond"], municipio, ["sobreexplotado"]),
            "ac_sup_no_sobreexplotado": sup_sum(details["ac_cond"], municipio, ["no explotado", "no sobreexplotado"]),
            "ac_pct_no_sobreexplotado": pct_sum(details["ac_cond"], municipio, ["no explotado", "no sobreexplotado"]),
            "salud_total_unidades": ctx.get("salud_total_puntos_muni", "ND"),
            "ene_conteo_total_municipio": ctx.get("ie_conteo_total_municipio", "ND"),
            "ene_linea_transm_l_km": fmt(
                municipal_value(details["linea_transm_l"], municipio, "longitud_km_total_municipio"),
                field_name="longitud_km_total_municipio",
            ),
        })
        ctx["anp_texto_automatico"] = build_anp_text(ctx)
        ctx["ene_linea_transm_l_texto"] = build_linea_transmision_text(
            municipal_value(details["linea_transm_l"], municipio, "longitud_km_total_municipio")
        )

        contexts.append(ctx)
    return contexts


def render(limit: Optional[int], compile_pdf: bool, keep_tex_only: bool) -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tex_dir = OUT_DIR / "tex"
    pdf_dir = OUT_DIR / "pdf"
    tex_dir.mkdir(exist_ok=True)
    pdf_dir.mkdir(exist_ok=True)
    write_placeholder_assets(OUT_DIR)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        variable_start_string="<<",
        variable_end_string=">>",
        block_start_string="<%",
        block_end_string="%>",
        comment_start_string="<#",
        comment_end_string="#>",
        autoescape=False,
    )
    template = env.get_template(TEMPLATE_NAME)
    template_text = (TEMPLATE_DIR / TEMPLATE_NAME).read_text(encoding="utf-8")
    variables = all_template_variables(template_text)

    contexts = build_contexts()
    if limit:
        contexts = contexts[:limit]

    rendered = []
    failed_compile = []
    for ctx in contexts:
        for var in variables:
            ctx.setdefault(var, "ND")
        slug = slugify(ctx["municipio"].replace(r"\_", "_"))
        tex_path = tex_dir / f"{slug}.tex"
        tex_path.write_text(template.render(**ctx), encoding="utf-8")
        rendered.append(tex_path)

        if compile_pdf:
            env_vars = dict(**os.environ)
            env_vars["TEXINPUTS"] = f".:{OUT_DIR}//:"
            cmd = [
                "latexmk", "-g", "-xelatex", "-interaction=nonstopmode", "-halt-on-error",
                f"-outdir={pdf_dir}", tex_path.name,
            ]
            result = subprocess.run(
                cmd,
                cwd=tex_dir,
                env=env_vars,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if result.returncode != 0:
                failed_compile.append({"tex": str(tex_path), "log": result.stdout[-4000:]})

    if keep_tex_only:
        compile_pdf = False

    return {
        "rendered": len(rendered),
        "compiled_requested": compile_pdf,
        "compile_errors": failed_compile,
        "tex_dir": str(tex_dir),
        "pdf_dir": str(pdf_dir),
        "out_dir": str(OUT_DIR),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render de prueba Jinja2-LaTeX para cuadernillos municipales.")
    parser.add_argument("--limit", type=int, default=None, help="Limita la cantidad de municipios para pruebas.")
    parser.add_argument("--compile", action="store_true", help="Compila los .tex renderizados con latexmk/xelatex.")
    parser.add_argument("--tex-only", action="store_true", help="Solo renderiza .tex.")
    args = parser.parse_args()

    result = render(args.limit, args.compile, args.tex_only)
    print(f"Renderizados: {result['rendered']}")
    print(f"TEX: {result['tex_dir']}")
    print(f"PDF: {result['pdf_dir']}")
    print(f"Errores de compilación: {len(result['compile_errors'])}")
    for err in result["compile_errors"][:5]:
        print(f"\nERROR {err['tex']}\n{err['log']}")


if __name__ == "__main__":
    main()
