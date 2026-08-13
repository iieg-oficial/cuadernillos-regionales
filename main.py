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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--municipio", type=str, default=None)
    parser.add_argument("--prod", action="store_true")
    parser.add_argument("--desde", type=str, default=None)
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

    municipios = get_all_municipio_ids()
    if args.desde:
        if args.desde not in municipios:
            raise SystemExit(f"Municipio '{args.desde}' no está en el catálogo")
        municipios = municipios[municipios.index(args.desde) :]
        Logger.info(f"Reanudando desde {args.desde} ({len(municipios)} pendientes)")

    for municipio_id in municipios:
        run(municipio_id, pipeline, args.prod)


if __name__ == "__main__":
    main()
