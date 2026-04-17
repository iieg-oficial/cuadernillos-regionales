import argparse

from core.compiler import compile
from core.pipelines.pipeline import Pipeline
from core.renderer import render
from core.utils.logger import Logger

from pipelines.demografia.pipeline import Demografia


def run(municipio_id: str, pipeline: Pipeline) -> None:
    Logger.info(f"Processing municipio: {municipio_id}")
    context = pipeline.run(municipio_id)
    tex_path = render(municipio_id, context)
    compile(tex_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--municipio", type=str, default=None)
    args = parser.parse_args()

    pipeline = Pipeline(
        sections=[
            Demografia(),
        ]
    )

    if args.municipio:
        run(args.municipio, pipeline)
    else:
        Logger.warning(
            "No municipio list defined yet — add sections and a municipio source."
        )


if __name__ == "__main__":
    main()
