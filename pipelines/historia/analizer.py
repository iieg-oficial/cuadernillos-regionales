from pathlib import Path

from core.constants import ND
from core.pipelines.stage import Stage
from core.utils.logger import Logger

MAPA_PLACEHOLDER = Path("templates/assets/mapa_placeholder.png")


def _normalize(text: str) -> str:
    text = text.replace("\x0c", " ")
    lines = [line.strip() for line in text.splitlines()]
    paragraphs = []
    buf = []
    for i, line in enumerate(lines):
        if not line:
            continue
        buf.append(line)
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
        last_char = line[-1] if line else ""
        first_next = next_line[0] if next_line else ""
        if last_char in ".!?:" and (not next_line or first_next.isupper()):
            paragraphs.append(" ".join(buf))
            buf = []
    if buf:
        paragraphs.append(" ".join(buf))
    return "\n\n".join(paragraphs)


def _mapa_latex(path: Path, nombre: str) -> str:
    return (
        "\\begin{figure}[H]\n"
        "\\refstepcounter{mapa}%\n"
        "\\noindent Mapa \\themapa\\\\\n"
        f"\\textbf{{Localización geográfica de {nombre}, Jalisco}}"
        "\\par\\vspace{4pt}\n"
        "\\centering\n"
        f"\\includegraphics[width=0.85\\textwidth]{{{path}}}\n"
        "\\end{figure}\n"
        "\\par\\vspace{-4pt}\\parbox{\\linewidth}{\\footnotesize\n"
        "Fuente: IIEG. Mapa General del Estado de Jalisco, 2026.}"
    )


class Analizer(Stage):
    def __init__(self, municipio_id: str):
        self.municipio_id = municipio_id

    def execute(self, input_data: dict) -> dict:
        Logger.info("Historia: procesando texto")
        toponimia = _normalize(input_data.get("toponimia") or "") or ND
        contexto = _normalize(input_data.get("contexto_historico") or "") or ND
        mapa_path = input_data.get("mapa_path") or MAPA_PLACEHOLDER
        nombre = input_data.get("municipio_nombre", "")

        Logger.info("Historia: análisis completo")
        return {
            "hi_toponimia": toponimia,
            "hi_contexto_historico": contexto,
            "hi_mapa_localizacion": _mapa_latex(mapa_path, nombre),
        }
