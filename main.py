import argparse

from core.compiler import compile, compile_prod
from core.pipelines.pipeline import Pipeline
from core.renderer import render
from core.utils.logger import Logger
from core.utils.municipalities import get_all_municipio_ids
from pipelines.demografia.pipeline import Demografia
from pipelines.directorio_municipal.pipeline import DirectorioMunicipal
from pipelines.economia.pipeline import Economia
from pipelines.geografia.pipeline import Geografia
from pipelines.gobierno_y_seguridad.pipeline import GobiernoYSeguridad
from pipelines.historia.pipeline import Historia


def run(municipio_id: str, pipeline: Pipeline, prod: bool = False) -> None:
    Logger.info(f"Processing municipio: {municipio_id}")
    context = pipeline.run(municipio_id)
    tex_path = render(municipio_id, context)
    if prod:
        compile_prod(tex_path)
    else:
        compile(tex_path)


def _acotar(municipios: list[str], desde: str | None, hasta: str | None) -> list[str]:
    for clave in (desde, hasta):
        if clave and clave not in municipios:
            raise SystemExit(f"Municipio '{clave}' no está en el catálogo")

    inicio = municipios.index(desde) if desde else 0
    fin = municipios.index(hasta) + 1 if hasta else len(municipios)
    if inicio >= fin:
        raise SystemExit(f"Rango vacío: '{desde}' va después de '{hasta}'")

    acotado = municipios[inicio:fin]
    if desde or hasta:
        Logger.info(
            f"Procesando {len(acotado)} municipios, de {acotado[0]} a {acotado[-1]}"
        )
    return acotado


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--municipio", type=str, default=None)
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

    if args.municipio:
        run(args.municipio, pipeline, args.prod)
        return

    municipios = _acotar(get_all_municipio_ids(), args.desde, args.hasta)
    for municipio_id in municipios:
        run(municipio_id, pipeline, args.prod)


if __name__ == "__main__":
    main()
