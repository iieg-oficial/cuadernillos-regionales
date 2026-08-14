import re
import tempfile
import zipfile
from pathlib import Path

import gdown

from core.settings import AppSettings
from core.utils.logger import Logger

ESCUDOS_DIR = Path("assets/escudos_mun_jal")
EXTENSIONS = (".png", ".jpg", ".jpeg")
DRIVE_ID_RE = re.compile(r"/d/([\w-]+)|[?&]id=([\w-]+)")


def _drive_id(url: str) -> str | None:
    match = DRIVE_ID_RE.search(url)
    if not match:
        return None
    return match.group(1) or match.group(2)


def _has_escudos() -> bool:
    return ESCUDOS_DIR.exists() and any(
        f.suffix.lower() in EXTENSIONS for f in ESCUDOS_DIR.iterdir()
    )


def ensure_escudos() -> None:
    if _has_escudos():
        return

    url = AppSettings().ESCUDOS_URL
    if not url:
        Logger.warning("ESCUDOS_URL sin configurar, no se descargan los escudos")
        return

    file_id = _drive_id(url)
    if not file_id:
        Logger.warning(f"ESCUDOS_URL sin identificador de Drive: {url}")
        return

    Logger.info("Descargando escudos municipales desde Google Drive")
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "escudos.zip"
        gdown.download(id=file_id, output=str(zip_path), quiet=True)
        if not zip_path.exists():
            Logger.error("No se pudo descargar el zip de escudos")
            return
        ESCUDOS_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            for member in zf.infolist():
                filename = Path(member.filename).name
                if not filename.lower().endswith(EXTENSIONS):
                    continue
                with zf.open(member) as src, (ESCUDOS_DIR / filename).open("wb") as dst:
                    dst.write(src.read())

    if not _has_escudos():
        Logger.error("El zip de escudos no contenía imágenes")
        return
    Logger.info(f"Escudos descargados ({len(list(ESCUDOS_DIR.iterdir()))} archivos)")


def escudo_path(municipio_id: str) -> Path | None:
    cvegeo = f"14{int(municipio_id):03d}"
    for ext in EXTENSIONS:
        candidate = ESCUDOS_DIR / f"{cvegeo}{ext}"
        if candidate.exists():
            return candidate
    Logger.warning(f"Escudo no encontrado para el municipio {cvegeo}")
    return None
