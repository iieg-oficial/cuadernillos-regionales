
# Muestra representativa: metropolitanos, costa, sierra, altos y municipios pequeños
SAMPLE := "1 12 17 32 56 67 97 98 101 120"

default:
    just --list --unsorted

# Instala dependencias y configura el entorno completo
[group("setup")]
setup:
    uv sync
    chmod +x .githooks/*
    pre-commit install
    pre-commit install --hook-type commit-msg

# Genera los cuadernillos de todos los municipios
[group("reports")]
run:
    uv run python main.py

# Genera el cuadernillo de un municipio específico
[group("reports")]
run-one clave:
    uv run python main.py --municipio {{clave}}

# Genera los cuadernillos de una muestra representativa de municipios
[group("reports")]
run-sample:
    #!/usr/bin/env bash
    set -euo pipefail
    for clave in {{ SAMPLE }}; do
        echo "==> $clave"
        uv run python main.py --municipio "$clave"
    done

# abre un archivo específico
[group("reports")]
open-one clave:
   open "$(ls -t output/pdf/{{clave}}_*cuadernillo*/*.pdf | head -1)"

# Revisa estilo y formato con ruff
[group("format code")]
lint:
    uv run ruff check .
    uv run ruff format --check .

# Corrige automáticamente los errores de estilo y formato
[group("format code")]
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Ejecuta la suite de pruebas
[group("test")]
test:
    uv run pytest
