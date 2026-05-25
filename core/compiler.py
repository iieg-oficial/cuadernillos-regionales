import subprocess
from pathlib import Path

from core.utils.logger import Logger


def compile(tex_path: Path) -> Path:
    output_dir = Path("output/pdf") / tex_path.parent.name
    output_dir.mkdir(parents=True, exist_ok=True)

    Logger.info(f"Compilando PDF con xelatex ({tex_path.name})...")
    cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        f"-output-directory={output_dir}",
        str(tex_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    pdf_path = output_dir / tex_path.with_suffix(".pdf").name

    if result.returncode != 0:
        if not pdf_path.exists():
            Logger.error(f"xelatex failed for {tex_path.name}:\n{result.stdout}")
            raise RuntimeError(f"xelatex failed for {tex_path.name}")
        Logger.warning(f"xelatex warnings for {tex_path.name} (PDF still generated)")

    Logger.info(f"PDF generated: {pdf_path}")
    return pdf_path
