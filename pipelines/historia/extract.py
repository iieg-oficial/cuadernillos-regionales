import json
import re
import ssl
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import gdown

from core.pipelines.stage import Stage
from core.settings import HistoriaSettings
from core.utils.logger import Logger
from core.utils.maps import get_draft_path

CATALOG_PATH = Path("assets/catalogs/historia.json")
MAPS_DIR = Path("assets/maps/historia")
TOTAL_MUNICIPIOS = 125
INDEX_URL = "https://iieg.gob.mx/ns/?page_id=21707"

NEXT_SECTION_PATTERNS = [
    "\x0cGeograf",
    "Geografía y Medio Ambiente",
    "GEOGRAFÍA",
    "\x0cDemograf",
    "\x0cEconom",
]

NOISE_PATTERNS = [
    re.compile(r"Figura \d+\.[^\n]*\n"),
    re.compile(r"Localización geográfica\.\n"),
    re.compile(r"Elaboración del IIEG\.[^\n]*\n"),
    re.compile(r"Página \d+\n"),
]


def _ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _fetch_pdf_links() -> dict[str, str]:
    ctx = _ssl_context()
    with urllib.request.urlopen(INDEX_URL, timeout=30, context=ctx) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    pattern = re.compile(
        r'href=["\']('
        + re.escape("https://iieg.gob.mx")
        + r'[^"\']*\.pdf[^"\']*)["\'][^>]*>([^<]+)',
        re.IGNORECASE,
    )
    links = {}
    for url, name in pattern.findall(html):
        links[name.strip()] = url
    return links


def _extract_historia_from_pdf(url: str) -> str:
    ctx = _ssl_context()
    with urllib.request.urlopen(url, timeout=60, context=ctx) as resp:
        pdf_bytes = resp.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ["pdftotext", tmp_path, "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        text = result.stdout
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    parts = text.split("Toponimia")
    if len(parts) < 3:
        return ""

    content = "Toponimia" + parts[2]

    end_pos = len(content)
    for pat in NEXT_SECTION_PATTERNS:
        idx = content.find(pat)
        if idx != -1:
            end_pos = min(end_pos, idx)

    historia = content[:end_pos]

    for noise in NOISE_PATTERNS:
        historia = noise.sub("", historia)

    historia = re.sub(r"\n{3,}", "\n\n", historia)
    historia = historia.strip()

    ctx_marker = "Contexto histórico"
    if ctx_marker in historia:
        idx = historia.index(ctx_marker)
        toponimia = historia[:idx].replace("Toponimia", "", 1).strip()
        contexto = historia[idx + len(ctx_marker) :].strip()
    else:
        toponimia = historia.replace("Toponimia", "", 1).strip()
        contexto = ""

    return {"toponimia": toponimia, "contexto_historico": contexto}


def _load_municipios() -> dict[str, str]:
    regions_path = Path("assets/catalogs/regions.json")
    with regions_path.open() as f:
        data = json.load(f)
    mun_ids = {}
    for region in data:
        for muns in region.values():
            for m in muns:
                mun_ids[m["municipio"]] = str(m["id"]).zfill(3)
    return mun_ids


def _get_nombre(municipio_id: str) -> str:
    regions_path = Path("assets/catalogs/regions.json")
    with regions_path.open() as f:
        data = json.load(f)
    for region in data:
        for muns in region.values():
            for m in muns:
                if str(m["id"]).zfill(3) == municipio_id:
                    return m["municipio"]
    return ""


def _build_catalog(pdf_links: dict[str, str], mun_ids: dict[str, str]) -> dict:
    catalog = {}
    for mun_name, mun_id in mun_ids.items():
        url = pdf_links.get(mun_name)
        if not url:
            catalog[mun_id] = {"texto": ""}
            continue
        try:
            texto = _extract_historia_from_pdf(url)
        except Exception:
            texto = ""
        if isinstance(texto, dict):
            catalog[mun_id] = texto
        else:
            catalog[mun_id] = {"toponimia": texto, "contexto_historico": ""}
    return catalog


def _download_maps() -> None:
    settings = HistoriaSettings()
    if not settings.HISTORIA_MAPS_URL:
        return
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "ubicacion.zip"
        gdown.download(url=settings.HISTORIA_MAPS_URL, output=str(zip_path), quiet=True)
        with zipfile.ZipFile(zip_path) as zf:
            for member in zf.infolist():
                if member.is_dir():
                    continue
                filename = Path(member.filename).name
                if not filename.endswith(".png"):
                    continue
                with zf.open(member) as src, (MAPS_DIR / filename).open("wb") as dst:
                    dst.write(src.read())
    n = len(list(MAPS_DIR.glob("ubicacion_*.png")))
    Logger.info(f"Mapas de historia descargados ({n} archivos)")


def _find_map(municipio_id: str) -> Path | None:
    if not MAPS_DIR.exists():
        return None
    p = MAPS_DIR / f"ubicacion_14{municipio_id}.png"
    if not p.exists():
        return None
    settings = HistoriaSettings()
    if settings.HISTORIA_MAPS_QUALITY == "draft":
        return get_draft_path(p, f"historia/14{municipio_id}", "hi_ubicacion")
    return p


class Extract(Stage):
    def execute(self, input_data: str = None) -> dict:
        municipio_id = str(input_data).zfill(3)

        if not CATALOG_PATH.exists():
            Logger.info("Historia: generando catálogo desde PDFs")
            mun_ids = _load_municipios()
            pdf_links = _fetch_pdf_links()
            catalog = _build_catalog(pdf_links, mun_ids)
            CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with CATALOG_PATH.open("w", encoding="utf-8") as f:
                json.dump(catalog, f, ensure_ascii=False, indent=2)

        if len(list(MAPS_DIR.glob("ubicacion_*.png"))) < TOTAL_MUNICIPIOS:
            Logger.info("Historia: descargando mapas")
            _download_maps()

        Logger.info("Historia: extrayendo datos del catálogo")
        with CATALOG_PATH.open(encoding="utf-8") as f:
            catalog = json.load(f)

        entry = catalog.get(municipio_id, {})
        return {
            "toponimia": entry.get("toponimia", ""),
            "contexto_historico": entry.get("contexto_historico", ""),
            "mapa_path": _find_map(municipio_id),
            "municipio_nombre": _get_nombre(municipio_id),
        }
