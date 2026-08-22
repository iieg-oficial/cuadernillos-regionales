import shutil
import subprocess
import tempfile
from pathlib import Path

from core.bundle import build, pack
from core.utils.logger import Logger

PROD_DIR = Path("output/pdf/prod")


def _run_xelatex(
    tex_path: Path, output_dir: Path, cwd: Path | None = None
) -> subprocess.CompletedProcess:
    nombre = tex_path.name if cwd else str(tex_path)
    cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        f"-output-directory={output_dir.resolve()}",
        nombre,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def _check(result, tex_path: Path, pdf_path: Path) -> None:
    if result.returncode == 0:
        return
    if not pdf_path.exists():
        Logger.error(f"xelatex failed for {tex_path.name}:\n{result.stdout}")
        raise RuntimeError(f"xelatex failed for {tex_path.name}")
    Logger.warning(f"xelatex warnings for {tex_path.name} (PDF still generated)")


def compile(tex_path: Path) -> Path:
    output_dir = Path("output/pdf") / tex_path.parent.name
    output_dir.mkdir(parents=True, exist_ok=True)

    Logger.info(f"Compilando PDF con xelatex ({tex_path.name})")
    result = _run_xelatex(tex_path, output_dir)

    pdf_path = output_dir / tex_path.with_suffix(".pdf").name
    _check(result, tex_path, pdf_path)

    Logger.info(f"PDF generated: {pdf_path}")
    return pdf_path


def compile_prod(tex_path: Path) -> Path:
    PROD_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = PROD_DIR / tex_path.with_suffix(".pdf").name

    Logger.info(f"Compilando PDF final con xelatex, dos pasadas ({tex_path.name})")
    bundle = build(tex_path)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        _run_xelatex(tex_path, tmp_dir, cwd=bundle)
        result = _run_xelatex(tex_path, tmp_dir, cwd=bundle)

        tmp_pdf = tmp_dir / tex_path.with_suffix(".pdf").name
        _check(result, tex_path, tmp_pdf)
        shutil.copy2(tmp_pdf, pdf_path)

    pack(bundle)

    Logger.info(f"PDF generated: {pdf_path}")
    return pdf_path
