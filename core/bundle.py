import re
import shutil
import zipfile
from pathlib import Path

from core.settings import AppSettings
from core.utils.logger import Logger

FONTS_DIR = "fonts"

# Sobras de una compilacion previa dentro del paquete: no van al zip.
AUXILIARES = {".aux", ".log", ".out", ".toc", ".pdf", ".gz", ".fls", ".fdb_latexmk"}

# Para latexmk. Overleaf NO lo usa para elegir el motor: ahi el compilador sale del
# menu del proyecto y hay que ponerlo en XeLaTeX a mano, como dice el LEEME.
LATEXMKRC = "$pdf_mode = 5;\n"

LEEME = """# {slug}

Cuadernillo municipal listo para compilar.

## Overleaf

**Hay que cambiar el compilador a XeLaTeX. Es el paso que no se puede saltar.**

1. En Overleaf: **New Project -> Upload Project** y sube `{slug}.zip`, el
   comprimido donde viene este archivo. Súbelo como proyecto nuevo, no arrastres su
   contenido a uno existente: ahí queda un `main.tex` de plantilla y Overleaf compila
   ese en vez de este.
2. **Menu -> Compiler -> XeLaTeX**, y vuelve a compilar.
3. El archivo principal es `{slug}.tex`. Si Overleaf abre otro, cámbialo en
   **Menu -> Main document**.

:warning: **Warning:** Overleaf compila con pdfLaTeX por omisión y elige el motor desde
ese menú: **ignora** tanto el `latexmkrc` que viene aquí como el comentario
`% !TEX program` de la primera línea del `.tex`. Si no lo cambias, falla con
`Fatal Package fontspec Error: The fontspec package requires either XeTeX or LuaTeX.`

:memo: **Note:** el documento usa `fontspec` para las tipografías Lexend y Garet, y
`fontspec` solo corre en XeLaTeX o LuaLaTeX.

## Local

    xelatex {slug}.tex
    xelatex {slug}.tex

Dos pasadas: la primera resuelve el indice y las referencias a mapas, la segunda
las escribe. Con `latexmk` basta una llamada; el `latexmkrc` ya selecciona XeLaTeX.

## Que hay aqui

- `{slug}.tex` documento completo, con el preambulo incluido
- `fonts/` tipografias Lexend y Garet
- `templates/assets/` portadas, logos y portadillas de seccion
- `assets/maps/`, `output/maps/` mapas
- `output/charts/` graficas
- `assets/escudos_mun_jal/` escudo del municipio

Las rutas son relativas a esta carpeta: si se mueve un archivo de lugar, hay que
ajustar el `.tex`.
"""

# \includegraphics directo y los macros de mapa, que reciben la ruta y arman el
# \includegraphics por dentro.
_INCLUDE = re.compile(
    r"\\(?:includegraphics|mapageo|mapafijo)(?:\[[^\]]*\])?"
    r"\{([^{}]*(?:\{[^{}]*\})?[^{}]*)\}"
)
_DETOKENIZE = re.compile(r"\\detokenize\{([^{}]*)\}")
_FONT_FILE = re.compile(r"[\w-]+\.(?:ttf|otf|TTF|OTF)")


def _graphics_paths(tex: str) -> set[str]:
    rutas = set()
    for arg in _INCLUDE.findall(tex):
        detok = _DETOKENIZE.search(arg)
        rutas.add((detok.group(1) if detok else arg).strip())
    return {r for r in rutas if r and "#" not in r and not r.startswith("/")}


def _copy_graphics(tex: str, destino: Path) -> tuple[int, list[str]]:
    copiados, faltantes = 0, []
    for ruta in sorted(_graphics_paths(tex)):
        origen = Path(ruta)
        if not origen.is_file():
            faltantes.append(ruta)
            continue
        final = destino / ruta
        final.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, final)
        copiados += 1
    return copiados, faltantes


def _copy_fonts(tex: str, destino: Path) -> tuple[int, list[str]]:
    origen_dir = Path(AppSettings().FONTS_PATH)
    copiados, faltantes = 0, []
    for nombre in sorted(set(_FONT_FILE.findall(tex))):
        origen = origen_dir / nombre
        if not origen.is_file():
            faltantes.append(nombre)
            continue
        (destino / FONTS_DIR).mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino / FONTS_DIR / nombre)
        copiados += 1
    return copiados, faltantes


def pack(destino: Path) -> Path:
    zip_path = destino.with_suffix(".zip")
    zip_path.unlink(missing_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for archivo in sorted(destino.rglob("*")):
            if not archivo.is_file() or archivo.suffix in AUXILIARES:
                continue
            z.write(archivo, archivo.relative_to(destino))
    shutil.rmtree(destino)
    mb = zip_path.stat().st_size / 1024 / 1024
    Logger.info(f"Paquete comprimido: {zip_path} ({mb:.0f} MB)")
    return zip_path


def build(tex_path: Path) -> Path:
    destino = tex_path.parent
    tex = tex_path.read_text()

    graficos, sin_grafico = _copy_graphics(tex, destino)
    fuentes, sin_fuente = _copy_fonts(tex, destino)

    (destino / "latexmkrc").write_text(LATEXMKRC)
    (destino / "LEEME.md").write_text(LEEME.format(slug=tex_path.stem))

    for falta in sin_grafico + sin_fuente:
        Logger.warning(f"Falta en el paquete de {destino.name}: {falta}")

    Logger.info(
        f"Paquete armado en {destino}: {graficos} imágenes y {fuentes} tipografías"
    )
    return destino
