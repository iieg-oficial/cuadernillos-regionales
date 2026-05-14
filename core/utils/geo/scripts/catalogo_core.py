#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Cataloga mapas y graficas municipales para el render LaTeX/Jinja."""

from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


# =========================
# Configuracion ajustable
# =========================

ROOT = Path(__file__).resolve().parents[1]
MAPAS_ROOT = ROOT / "mapas"
GRAFICAS_ROOT = ROOT / "graficas"
DATOS_ESTADISTICOS_ROOT = ROOT / "datos_estadisticos"
SALIDA_CATALOGOS = ROOT / "catalogos"
RUTA_BASE_RELATIVA = ROOT
TEMPLATE_TEX = ROOT / "latex" / "templates" / "main.tex"
EXTENSIONES_VALIDAS = {".png", ".jpg", ".jpeg", ".pdf"}

CATALOGO_MAPAS = "catalogo_mapas.csv"
CATALOGO_GRAFICAS = "catalogo_graficas.csv"
REPORTE = "reporte_catalogo_insumos.md"

# Alias entre nombres de carpetas/archivos y variables actuales del template.
TEMA_A_VARIABLE = {
    "acuiferos": "ac",
    "anp": "anp",
    "clima": "cl",
    "clima_koppen": "cl",
    "cuencas": "cu",
    "edafologia": "ed",
    "educacion": "edu",
    "energia": "ie",
    "erosion_efec": "ee",
    "erosion_efectiva": "ee",
    "erosion_pot": "er",
    "erosion_potencial": "er",
    "espacio_pub": "ep",
    "geologia": "geo",
    "itur": "itur",
    "itur_index_cat": "itur",
    "mapa_base": "base",
    "ndvi": "ndvi",
    "ndwi": "ndwi",
    "pendiente_clasificada": "tp",
    "pendientes": "tp",
    "precipitacion": "pp",
    "precipitacion_hist": "pp",
    "salud": "salud",
    "sequia": "ds",
    "temperatura": "tm",
    "temperatura_hist": "tm",
    "ubicacion": "ubicacion",
    "ubicacion_c_fondo": "ubicacion_c_fondo",
    "ubicacion_s_fondo": "ubicacion_s_fondo",
    "uso_suelo": "usv",
    "vientos_dominantes": "dg_viento",
}

VARIABLES_NO_MUNICIPALES = {
    "logo_header",
    "logo_footer",
    "portada",
}


@dataclass(frozen=True)
class MunicipioIndex:
    municipios: pd.DataFrame
    by_clave: dict[str, dict[str, str]]
    by_clave3: dict[str, dict[str, str]]
    by_norm: dict[str, dict[str, str]]


def normalizar_texto(value: object, sep: str = "_") -> str:
    """Normaliza texto para comparar nombres de municipio, tema y archivo."""
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", sep, text)
    return text.strip(sep)


def clave_geo_texto(value: object) -> str:
    """Conserva clave geo como texto de cinco digitos cuando es posible."""
    if value is None or pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return str(value).strip()
    if len(digits) <= 3:
        return f"14{digits.zfill(3)}"
    return digits.zfill(5)


def municipio_index_from_dataframe(df: pd.DataFrame) -> MunicipioIndex:
    """Construye indices municipales desde una tabla ya generada."""
    df = df.copy()
    if "nombre" in df.columns and "municipio" not in df.columns:
        df = df.rename(columns={"nombre": "municipio"})
    if "dg_nombre" in df.columns and "municipio" not in df.columns:
        df["municipio"] = df["dg_nombre"]
    if "dg_clave_geo" in df.columns and "clave_geo" not in df.columns:
        df["clave_geo"] = df["dg_clave_geo"]
    if "clave_geo" not in df.columns or "municipio" not in df.columns:
        raise ValueError("La tabla municipal debe contener clave_geo/municipio o dg_clave_geo/dg_nombre.")

    df = df[["clave_geo", "municipio"]].dropna(how="all").copy()
    df["clave_geo"] = df["clave_geo"].map(clave_geo_texto)
    df["municipio"] = df["municipio"].astype(str).str.strip()
    df["municipio_norm"] = df["municipio"].map(normalizar_texto)
    df = df[df["clave_geo"].ne("") & df["municipio"].ne("")]
    df = df.drop_duplicates("clave_geo").sort_values("municipio")

    records = df.to_dict("records")
    by_clave = {row["clave_geo"]: row for row in records}
    by_clave3 = {row["clave_geo"][-3:]: row for row in records}
    by_norm = {row["municipio_norm"]: row for row in records}
    return MunicipioIndex(df, by_clave, by_clave3, by_norm)


def municipio_index_from_estadisticas(root: Path) -> MunicipioIndex:
    """Lee municipios desde las estadisticas ya generadas, sin PostGIS ni GPKG."""
    preferred = root / "descripcion_general" / "descripcion_general_variables_texto.csv"
    candidates = [preferred] if preferred.exists() else []
    candidates.extend(path for path in sorted(root.rglob("*_variables_texto.csv")) if path not in candidates)
    for path in candidates:
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
            return municipio_index_from_dataframe(df)
        except Exception:
            continue
    raise FileNotFoundError(
        "No se pudo construir el indice municipal. Se requiere "
        "datos_estadisticos/descripcion_general/descripcion_general_variables_texto.csv "
        "o una tabla *_variables_texto.csv con dg_clave_geo/dg_nombre."
    )


def leer_municipios(path: Path) -> MunicipioIndex:
    """Compatibilidad CLI: lee una tabla CSV municipal portable."""
    return municipio_index_from_dataframe(pd.read_csv(path, encoding="utf-8-sig"))


def tema_desde_path(path: Path, root: Path) -> str:
    """Obtiene tema desde la estructura relativa del archivo."""
    rel_parts = path.relative_to(root).parts
    if not rel_parts:
        return ""
    if rel_parts[0] == "ubicacion" and len(rel_parts) > 2:
        return f"ubicacion_{rel_parts[1]}"
    return rel_parts[0]


def listar_temas(root: Path, extensiones: set[str]) -> list[str]:
    """Lista carpetas tematicas con o sin archivos validos."""
    temas: set[str] = set()
    for directory in root.rglob("*"):
        if not directory.is_dir():
            continue
        rel = directory.relative_to(root)
        if not rel.parts:
            continue
        has_child_dirs = any(child.is_dir() for child in directory.iterdir())
        has_direct_files = any(
            child.is_file() and child.suffix.lower() in extensiones
            for child in directory.iterdir()
        )
        if has_child_dirs and not has_direct_files:
            continue
        if rel.parts[0] == "ubicacion" and len(rel.parts) > 1:
            temas.add(f"ubicacion_{rel.parts[1]}")
        elif len(rel.parts) == 1:
            temas.add(rel.parts[0])
    return sorted(temas)


def listar_archivos(root: Path, extensiones: set[str]) -> list[Path]:
    """Recorre recursivamente y devuelve archivos graficos validos."""
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in extensiones)


def parsear_variables_template(template: Path) -> pd.DataFrame:
    """Extrae llamadas a \\mapa y \\grafica con su variable Jinja asociada."""
    if not template.exists():
        return pd.DataFrame(columns=["tipo", "id_tex", "titulo", "variable_tex"])
    text = template.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\\(?P<tipo>mapa|grafica)\{(?P<id>[^{}]+)\}\{(?P<titulo>[^{}]+)\}\{<<\s*(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*>>\}",
        re.MULTILINE,
    )
    rows = []
    for match in pattern.finditer(text):
        rows.append({
            "tipo": match.group("tipo"),
            "id_tex": match.group("id"),
            "titulo": match.group("titulo"),
            "variable_tex": match.group("var"),
        })
    return pd.DataFrame(rows)


def variable_para_tema(tema: str, tipo: str, template_vars: pd.DataFrame) -> str:
    """Infiere variable LaTeX/Jinja para un tema y tipo de insumo."""
    alias = TEMA_A_VARIABLE.get(tema, normalizar_texto(tema))
    suffix = "mapa" if tipo == "mapa" else "grafica"
    candidate = f"{alias}_{suffix}"

    vars_tipo = template_vars[template_vars["tipo"] == ("mapa" if tipo == "mapa" else "grafica")]
    if candidate in set(vars_tipo["variable_tex"]):
        return candidate

    by_id = vars_tipo[vars_tipo["id_tex"].map(normalizar_texto) == normalizar_texto(alias)]
    if not by_id.empty:
        return str(by_id.iloc[0]["variable_tex"])
    return candidate


def inferir_municipio(path: Path, tema: str, index: MunicipioIndex) -> tuple[str, str, str]:
    """Relaciona un archivo con municipio por clave, clave de tres digitos o nombre normalizado."""
    stem_norm = normalizar_texto(path.stem)
    tokens = set(stem_norm.split("_"))

    for clave, row in index.by_clave.items():
        if clave in tokens or stem_norm.endswith(f"_{clave}") or stem_norm.startswith(f"{clave}_"):
            return row["clave_geo"], row["municipio"], "clave_geo"

    for clave3, row in index.by_clave3.items():
        if clave3 in tokens or stem_norm.endswith(f"_{clave3}") or stem_norm.startswith(f"{clave3}_"):
            return row["clave_geo"], row["municipio"], "clave_municipal_3d"

    # Quita posibles prefijos de tema antes de comparar el nombre del municipio.
    tema_norm = normalizar_texto(tema)
    candidates = {stem_norm}
    for prefix in {tema_norm, *normalizar_texto(tema).split("__")}:
        if prefix and stem_norm.startswith(prefix + "_"):
            candidates.add(stem_norm[len(prefix) + 1 :])

    for mun_norm, row in sorted(index.by_norm.items(), key=lambda item: len(item[0]), reverse=True):
        if mun_norm in candidates or stem_norm.endswith("_" + mun_norm):
            return row["clave_geo"], row["municipio"], "nombre_municipio"
    return "", "", "pendiente_revision_manual"


def relpath_posix(path: Path, base: Path) -> str:
    """Calcula ruta relativa POSIX aun cuando no comparten padre inmediato."""
    return Path(os.path.relpath(path.resolve(), base.resolve())).as_posix()


def catalogar(
    root: Path,
    tipo: str,
    index: MunicipioIndex,
    template_vars: pd.DataFrame,
    base_relativa: Path,
    extensiones: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Construye catalogo municipal-tema, archivos encontrados y pendientes."""
    temas = listar_temas(root, extensiones)
    files = listar_archivos(root, extensiones)

    found_rows = []
    for path in files:
        tema = tema_desde_path(path, root)
        clave, municipio, metodo = inferir_municipio(path, tema, index)
        variable = variable_para_tema(tema, tipo, template_vars)
        found_rows.append({
            "clave_geo": clave,
            "municipio": municipio,
            "tema": tema,
            "variable_tex": variable,
            "path_absoluto": str(path.resolve()),
            "path_relativo": relpath_posix(path, base_relativa),
            "existe": bool(clave and municipio),
            "tipo_archivo": path.suffix.lower().lstrip("."),
            "metodo_inferencia": metodo,
        })

    encontrados = pd.DataFrame(found_rows)
    pendientes = encontrados[encontrados["clave_geo"].eq("")].copy() if not encontrados.empty else pd.DataFrame()
    vinculados = encontrados[encontrados["clave_geo"].ne("")].copy() if not encontrados.empty else pd.DataFrame()

    if not vinculados.empty:
        prioridad = {"pdf": 0, "png": 1, "jpg": 2, "jpeg": 3}
        seleccion = vinculados.copy()
        seleccion["_prioridad"] = seleccion["tipo_archivo"].map(prioridad).fillna(99)
        seleccion = (
            seleccion.sort_values(["clave_geo", "tema", "_prioridad", "path_absoluto"])
            .drop_duplicates(["clave_geo", "tema"], keep="first")
            .drop(columns="_prioridad")
        )
    else:
        seleccion = pd.DataFrame()

    expected_rows = []
    for _, mun in index.municipios.iterrows():
        for tema in temas:
            variable = variable_para_tema(tema, tipo, template_vars)
            expected_rows.append({
                "clave_geo": mun["clave_geo"],
                "municipio": mun["municipio"],
                "tema": tema,
                "variable_tex": variable,
            })
    catalogo = pd.DataFrame(expected_rows, columns=["clave_geo", "municipio", "tema", "variable_tex"])

    if seleccion.empty:
        for col in ["path_absoluto", "path_relativo", "tipo_archivo", "metodo_inferencia"]:
            catalogo[col] = ""
        catalogo["existe"] = False
    else:
        cols = [
            "clave_geo", "tema", "path_absoluto", "path_relativo", "tipo_archivo",
            "metodo_inferencia",
        ]
        catalogo = catalogo.merge(seleccion[cols], on=["clave_geo", "tema"], how="left")
        catalogo["existe"] = catalogo["path_absoluto"].notna()
        fill_cols = ["path_absoluto", "path_relativo", "tipo_archivo", "metodo_inferencia"]
        catalogo[fill_cols] = catalogo[fill_cols].fillna("")

    ordered = [
        "clave_geo", "municipio", "tema", "variable_tex", "path_absoluto",
        "path_relativo", "existe", "tipo_archivo", "metodo_inferencia",
    ]
    return catalogo[ordered], encontrados, pendientes


def variables_sin_archivo(catalogo: pd.DataFrame, template_vars: pd.DataFrame, tipo: str) -> pd.DataFrame:
    """Detecta variables del template que no tienen archivo asociado en catalogo."""
    suffix = "_mapa" if tipo == "mapa" else "_grafica"
    vars_tipo = template_vars[template_vars["tipo"] == ("mapa" if tipo == "mapa" else "grafica")].copy()
    vars_tipo = vars_tipo[~vars_tipo["variable_tex"].isin(VARIABLES_NO_MUNICIPALES)]
    existentes = set(catalogo.loc[catalogo["existe"], "variable_tex"])
    out = vars_tipo[~vars_tipo["variable_tex"].isin(existentes)].copy()
    out = out[out["variable_tex"].str.endswith(suffix) | out["variable_tex"].eq("dg_viento_grafica")]
    return out


def archivos_sin_variable(encontrados: pd.DataFrame, template_vars: pd.DataFrame) -> pd.DataFrame:
    """Detecta archivos cuyo tema no aparece como variable explicita en el template."""
    if encontrados.empty:
        return pd.DataFrame()
    vars_template = set(template_vars["variable_tex"])
    return encontrados[~encontrados["variable_tex"].isin(vars_template)].copy()


def temas_sin_graficas(catalogo_graficas: pd.DataFrame) -> pd.DataFrame:
    """Resume temas de graficas sin ningun archivo encontrado."""
    resumen = catalogo_graficas.groupby("tema", as_index=False)["existe"].sum()
    return resumen[resumen["existe"].eq(0)].rename(columns={"existe": "archivos_encontrados"})


def escribir_reporte(
    salida: Path,
    mapas: pd.DataFrame,
    graficas: pd.DataFrame,
    encontrados_mapas: pd.DataFrame,
    encontrados_graficas: pd.DataFrame,
    pendientes_mapas: pd.DataFrame,
    pendientes_graficas: pd.DataFrame,
    template_vars: pd.DataFrame,
) -> None:
    """Escribe reporte Markdown de validacion de catalogos."""
    mapas_vars_sin = variables_sin_archivo(mapas, template_vars, "mapa")
    graficas_vars_sin = variables_sin_archivo(graficas, template_vars, "grafica")
    mapas_sin_var = archivos_sin_variable(encontrados_mapas, template_vars)
    graficas_sin_var = archivos_sin_variable(encontrados_graficas, template_vars)
    temas_graf_sin = temas_sin_graficas(graficas)

    def resumen_catalogo(df: pd.DataFrame) -> str:
        esperados = len(df)
        encontrados = int(df["existe"].sum())
        faltantes = esperados - encontrados
        return f"- Esperados: {esperados}\n- Encontrados: {encontrados}\n- Faltantes: {faltantes}"

    def tabla_md(df: pd.DataFrame, cols: Iterable[str], limit: int = 40) -> str:
        if df.empty:
            return "_Sin registros._"
        view = df.loc[:, [c for c in cols if c in df.columns]].head(limit).fillna("")
        headers = list(view.columns)
        rows = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for _, row in view.iterrows():
            values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in headers]
            rows.append("| " + " | ".join(values) + " |")
        return "\n".join(rows)

    municipios_sin_mapa = mapas[~mapas["existe"]]
    municipios_sin_grafica = graficas[~graficas["existe"]]

    report = [
        "# Reporte de catalogo de insumos LaTeX",
        "",
        "## Mapas esperados vs encontrados",
        resumen_catalogo(mapas),
        "",
        "## Graficas esperadas vs encontradas",
        resumen_catalogo(graficas),
        "",
        "## Temas donde no se generaron graficas",
        tabla_md(temas_graf_sin, ["tema", "archivos_encontrados"]),
        "",
        "## Variables LaTeX sin archivo asociado",
        "### Mapas",
        tabla_md(mapas_vars_sin, ["id_tex", "titulo", "variable_tex"]),
        "",
        "### Graficas",
        tabla_md(graficas_vars_sin, ["id_tex", "titulo", "variable_tex"]),
        "",
        "## Archivos encontrados sin variable LaTeX asociada",
        "### Mapas",
        tabla_md(mapas_sin_var, ["tema", "variable_tex", "path_relativo", "metodo_inferencia"]),
        "",
        "### Graficas",
        tabla_md(graficas_sin_var, ["tema", "variable_tex", "path_relativo", "metodo_inferencia"]),
        "",
        "## Archivos pendientes de revision manual",
        "### Mapas",
        tabla_md(pendientes_mapas, ["tema", "path_absoluto", "metodo_inferencia"]),
        "",
        "### Graficas",
        tabla_md(pendientes_graficas, ["tema", "path_absoluto", "metodo_inferencia"]),
        "",
        "## Municipios sin mapa o grafica para algun tema",
        "### Mapas faltantes",
        tabla_md(municipios_sin_mapa, ["clave_geo", "municipio", "tema", "variable_tex"], limit=80),
        "",
        "### Graficas faltantes",
        tabla_md(municipios_sin_grafica, ["clave_geo", "municipio", "tema", "variable_tex"], limit=80),
        "",
        "## Integracion recomendada",
        (
            "El punto mas seguro es `build_contexts()` en "
            "`cuadernillos_iieg/260420_render_cuadernillos.py`, despues de inicializar "
            "`*_mapa` y `*_grafica` como `placeholder.png`. Leer los catalogos, filtrar "
            "por `clave_geo` y actualizar el contexto con `{variable_tex: path_relativo}` "
            "solo cuando `existe=True`. Para llamadas inexistentes, mantener placeholder "
            "o usar bloques Jinja condicionales; no conviene borrar llamadas de la plantilla."
        ),
    ]
    salida.write_text("\n".join(report) + "\n", encoding="utf-8")


def limpiar_llamadas_inexistentes(tex_path: Path, catalogo_graficas: pd.DataFrame, crear_bak: bool = True) -> Path:
    """Comenta llamadas \\grafica cuyo `variable_tex` no tiene archivo; crea .bak."""
    if crear_bak:
        backup = tex_path.with_suffix(tex_path.suffix + ".bak")
        shutil.copy2(tex_path, backup)

    existentes = set(catalogo_graficas.loc[catalogo_graficas["existe"], "variable_tex"])
    text = tex_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(?m)^(?P<linea>\\grafica\{[^{}]+\}\{[^{}]+\}\{<<\s*(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*>>\}\{[^{}]+\})"
    )

    def repl(match: re.Match[str]) -> str:
        if match.group("var") in existentes:
            return match.group("linea")
        return "% AUTO-CATALOG: llamada comentada por grafica inexistente\n%" + match.group("linea")

    tex_path.write_text(pattern.sub(repl, text), encoding="utf-8")
    return tex_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera catalogos de mapas y graficas para LaTeX.")
    parser.add_argument("--mapas-root", type=Path, default=MAPAS_ROOT)
    parser.add_argument("--graficas-root", type=Path, default=GRAFICAS_ROOT)
    parser.add_argument("--municipios-csv", type=Path, default=DATOS_ESTADISTICOS_ROOT / "descripcion_general" / "descripcion_general_variables_texto.csv")
    parser.add_argument("--salida", type=Path, default=SALIDA_CATALOGOS)
    parser.add_argument("--base-relativa", type=Path, default=RUTA_BASE_RELATIVA)
    parser.add_argument("--template-tex", type=Path, default=TEMPLATE_TEX)
    parser.add_argument("--extensiones", nargs="*", default=sorted(EXTENSIONES_VALIDAS))
    parser.add_argument("--limpiar-tex", type=Path, help="Comenta llamadas de graficas inexistentes en este .tex y crea .bak.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    extensiones = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in args.extensiones}

    args.salida.mkdir(parents=True, exist_ok=True)
    logging.info("Leyendo municipios: %s", args.municipios_csv)
    index = leer_municipios(args.municipios_csv)
    template_vars = parsear_variables_template(args.template_tex)

    logging.info("Catalogando mapas: %s", args.mapas_root)
    mapas, encontrados_mapas, pendientes_mapas = catalogar(
        args.mapas_root, "mapa", index, template_vars, args.base_relativa, extensiones
    )
    logging.info("Catalogando graficas: %s", args.graficas_root)
    graficas, encontrados_graficas, pendientes_graficas = catalogar(
        args.graficas_root, "grafica", index, template_vars, args.base_relativa, extensiones
    )

    mapas_path = args.salida / CATALOGO_MAPAS
    graficas_path = args.salida / CATALOGO_GRAFICAS
    reporte_path = args.salida / REPORTE

    mapas.to_csv(mapas_path, index=False, encoding="utf-8-sig")
    graficas.to_csv(graficas_path, index=False, encoding="utf-8-sig")
    escribir_reporte(
        reporte_path,
        mapas,
        graficas,
        encontrados_mapas,
        encontrados_graficas,
        pendientes_mapas,
        pendientes_graficas,
        template_vars,
    )

    if args.limpiar_tex:
        limpiar_llamadas_inexistentes(args.limpiar_tex, graficas)
        logging.info("Template actualizado con respaldo .bak: %s", args.limpiar_tex)

    logging.info("Catalogo mapas: %s", mapas_path)
    logging.info("Catalogo graficas: %s", graficas_path)
    logging.info("Reporte: %s", reporte_path)
    logging.info("Mapas encontrados: %s/%s", int(mapas["existe"].sum()), len(mapas))
    logging.info("Graficas encontradas: %s/%s", int(graficas["existe"].sum()), len(graficas))


if __name__ == "__main__":
    main()
