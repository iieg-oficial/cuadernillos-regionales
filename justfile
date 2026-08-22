
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
[group("dev")]
run:
    uv run python main.py

# Genera el cuadernillo de un municipio específico
[group("dev")]
run-one clave:
    uv run python main.py --municipio {{clave}}

# Genera los cuadernillos de una muestra representativa de municipios
[group("dev")]
run-sample:
    #!/usr/bin/env bash
    set -euo pipefail
    for clave in {{ SAMPLE }}; do
        echo "==> $clave"
        uv run python main.py --municipio "$clave"
    done

# abre un archivo específico
[group("dev")]
open-one clave:
   open "$(ls -t output/pdf/{{clave}}_*cuadernillo*/*.pdf | head -1)"

# Genera los cuadernillos finales en output/pdf/prod con dos pasadas de xelatex; reanuda desde una clave si se le pasa
[group("prod")]
prod-run desde="":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -n "{{ desde }}" ]; then
        uv run python main.py --prod --desde "{{ desde }}"
    else
        uv run python main.py --prod
    fi

# Genera un rango de cuadernillos finales por clave, ambos extremos incluidos
[group("prod")]
prod-run-range desde hasta:
    uv run python main.py --prod --desde {{desde}} --hasta {{hasta}}

# Genera un solo cuadernillo final en output/pdf/prod
[group("prod")]
prod-run-one clave:
    uv run python main.py --prod --municipio {{clave}}

# Abre un cuadernillo final de output/pdf/prod
[group("prod")]
prod-open-one clave:
    open "$(ls -t output/pdf/prod/{{clave}}_*.pdf | head -1)"

# Borra mapas y gráficas para volver a descargarlos o regenerarlos; pide confirmación
[group("mantenimiento")]
limpiar-mapas-y-graficas:
    #!/usr/bin/env bash
    set -euo pipefail
    dirs=(assets/maps output/maps output/charts)
    echo "Se va a borrar:"
    for d in "${dirs[@]}"; do
        if [ -d "$d" ]; then
            printf '  %-16s %s\n' "$d" "$(du -sh "$d" | cut -f1)"
        else
            printf '  %-16s (no existe)\n' "$d"
        fi
    done
    echo
    echo "assets/maps se vuelve a bajar de Drive en la siguiente corrida;"
    echo "output/maps y output/charts se regeneran solos."
    read -r -p "Escribe 'borrar' para confirmar: " respuesta
    if [ "$respuesta" != "borrar" ]; then
        echo "Cancelado, no se borró nada."
        exit 0
    fi
    rm -rf "${dirs[@]}"
    echo "Listo."

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
