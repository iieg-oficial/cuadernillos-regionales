import argparse

from core.compiler import compile, compile_prod
from core.pipelines.pipeline import Pipeline
from core.renderer import render
from core.utils.logger import Logger
from core.utils.regions import get_all_region_claves, normalize_clave
from pipelines.demografia.pipeline import Demografia
from pipelines.directorio_municipal.pipeline import DirectorioMunicipal
from pipelines.economia.pipeline import Economia
from pipelines.geografia.pipeline import Geografia
from pipelines.gobierno_y_seguridad.pipeline import GobiernoYSeguridad
from pipelines.historia.pipeline import Historia


def run(clave: str, pipeline: Pipeline, prod: bool = False) -> None:
    Logger.info(f"Processing region: {clave}")
    context = pipeline.run(clave)
    tex_path = render(clave, context, prod)
    if prod:
        compile_prod(tex_path)
    else:
        compile(tex_path)


def _normalizar_o_salir(valor: str | None) -> str | None:
    if not valor:
        return None
    try:
        return normalize_clave(valor)
    except ValueError:
        raise SystemExit(f"Región '{valor}' no está en el catálogo") from None


def _acotar(claves: list[str], desde: str | None, hasta: str | None) -> list[str]:
    for clave in (desde, hasta):
        if clave and clave not in claves:
            raise SystemExit(f"Región '{clave}' no está en el catálogo")

    inicio = claves.index(desde) if desde else 0
    fin = claves.index(hasta) + 1 if hasta else len(claves)
    if inicio >= fin:
        raise SystemExit(f"Rango vacío: '{desde}' va después de '{hasta}'")

    acotado = claves[inicio:fin]
    if desde or hasta:
        Logger.info(
            f"Procesando {len(acotado)} regiones, de {acotado[0]} a {acotado[-1]}"
        )
    return acotado


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, default=None)
    parser.add_argument("--prod", action="store_true")
    parser.add_argument("--desde", type=str, default=None)
    parser.add_argument("--hasta", type=str, default=None)
    args = parser.parse_args()

    pipeline = Pipeline(
        sections=[
            Historia(),
            Demografia(),
            DirectorioMunicipal(),
            Geografia(),
            Economia(),
            GobiernoYSeguridad(),
        ]
    )

    if args.region:
        run(_normalizar_o_salir(args.region), pipeline, args.prod)
        return

    claves = _acotar(
        get_all_region_claves(),
        _normalizar_o_salir(args.desde),
        _normalizar_o_salir(args.hasta),
    )
    for clave in claves:
        run(clave, pipeline, args.prod)


if __name__ == "__main__":
    main()
