import re
import shutil
from pathlib import Path

from core.settings import AppSettings
from core.utils.logger import Logger

FONTS_DIR = "fonts"

# Overleaf compila con pdfLaTeX por omision y este documento necesita XeLaTeX por
# fontspec. El latexmkrc se lo dice sin que nadie tenga que tocar la configuracion.
LATEXMKRC = "$pdf_mode = 5;\n"

LEEME = """# {slug}

Cuadernillo municipal listo para compilar.

## Overleaf

1. Comprime esta carpeta en un .zip.
2. New Project -> Upload Project y sube el .zip.
3. El archivo principal es `{slug}.tex`.

El `latexmkrc` ya deja seleccionado XeLaTeX, que es el que necesita el documento por las
tipografias. Si Overleaf no lo tomara: Menu -> Compiler -> XeLaTeX.

## Local

    xelatex {slug}.tex
    xelatex {slug}.tex

Dos pasadas: la primera resuelve el indice y las referencias a mapas, la segunda
las escribe.

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
        f"Paquete listo en {destino}: {graficos} imágenes y {fuentes} tipografías"
    )
    return destino
