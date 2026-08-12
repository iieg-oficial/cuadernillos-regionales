import tempfile
import zipfile
from pathlib import Path

import gdown

from core.settings import AppSettings
from core.utils.logger import Logger

ESCUDOS_DIR = Path("assets/escudos_mun_jal_png_con_fondo")
EXTENSIONS = (".png", ".jpg", ".jpeg")


def ensure_escudos() -> None:
    if ESCUDOS_DIR.exists():
        return

    url = AppSettings().ESCUDOS_URL
    if not url:
        Logger.warning("ESCUDOS_URL sin configurar, no se descargan los escudos")
        return

    ESCUDOS_DIR.mkdir(parents=True, exist_ok=True)
    Logger.info("Descargando escudos municipales desde Google Drive")
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "escudos.zip"
        gdown.download(url=url, output=str(zip_path), quiet=True, fuzzy=True)
        with zipfile.ZipFile(zip_path) as zf:
            for member in zf.infolist():
                filename = Path(member.filename).name
                if not filename.lower().endswith(EXTENSIONS):
                    continue
                with zf.open(member) as src, (ESCUDOS_DIR / filename).open("wb") as dst:
                    dst.write(src.read())
    Logger.info(f"Escudos descargados ({len(list(ESCUDOS_DIR.iterdir()))} archivos)")


def escudo_path(municipio_id: str) -> Path | None:
    cvegeo = f"14{int(municipio_id):03d}"
    for ext in EXTENSIONS:
        candidate = ESCUDOS_DIR / f"{cvegeo}{ext}"
        if candidate.exists():
            return candidate
    Logger.warning(f"Escudo no encontrado para el municipio {cvegeo}")
    return None
