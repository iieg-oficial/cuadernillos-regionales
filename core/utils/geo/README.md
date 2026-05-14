# Proceso de compilacion de cuadernillos

Version portable para la etapa editorial final. Parte de estadisticas CSV ya generadas y mapas PNG/PDF exportados; no carga capas, no consulta PostGIS, no procesa rasters y no calcula estadisticas espaciales.

## Estructura

- `datos_estadisticos/`: entrada con CSV ya generados. Debe incluir `descripcion_general/descripcion_general_variables_texto.csv`.
- `mapas/`: entrada con mapas exportados por municipio en PNG/JPG/PDF.
- `graficas/`: salida de graficas generadas desde los CSV.
- `catalogos/`: catalogos que vinculan mapas/graficas con variables LaTeX.
- `latex/templates/main.tex`: plantilla Jinja/LaTeX.
- `latex/assets/`: logos, portada y placeholder.
- `salidas/tex/`: archivos `.tex` renderizados.
- `salidas/pdf/`: PDF finales cuando se usa `--compile`.
- `logs/`: bitacoras del flujo.
- `scripts/`: modulos editoriales reutilizados.

## Instalacion

```bash
cd proceso_compilacion_cuadernillos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para compilar PDF se requiere una instalacion local de LaTeX con `latexmk` y `xelatex` disponibles en `PATH`.

## Entradas requeridas

1. Copiar o montar los CSV de estadisticas en `datos_estadisticos/`.
2. Copiar o montar los mapas exportados en `mapas/`.
3. Verificar la plantilla en `latex/templates/main.tex`.

Tambien se pueden definir rutas externas con variables de entorno:

```bash
export CUADERNILLOS_DATOS=/ruta/a/estadisticas
export CUADERNILLOS_MAPAS=/ruta/a/mapas
```

## Ejecucion

Renderizar `.tex` sin compilar PDF:

```bash
python run_compilacion.py
```

Compilar PDF:

```bash
python run_compilacion.py --compile
```

Prueba de un municipio:

```bash
python run_compilacion.py --municipio 001 --limit 1
```

Ejecutar solo catalogos y render:

```bash
python run_compilacion.py --skip-graficas --skip-variables
```

## Flujo

1. `generar_graficas.py`: lee `datos_estadisticos/` y escribe PNG en `graficas/`.
2. `generar_variables_texto.py`: consolida variables narrativas y valida variables usadas por la plantilla.
3. `generar_catalogo_mapas.py`: cataloga mapas exportados por municipio.
4. `generar_catalogo_graficas.py`: cataloga graficas generadas.
5. `render_latex.py`: construye contextos, renderiza `.tex` y opcionalmente compila PDF.

## Git

Los insumos pesados y salidas se ignoran por defecto en `.gitignore`: `datos_estadisticos/`, `mapas/`, `graficas/`, `catalogos/`, `salidas/` y `logs/`. Si se decide versionar insumos, usar Git LFS o un repositorio/artefacto separado.

## Riesgos conocidos

- El render requiere que existan todas las tablas `*_detalle.csv` esperadas por `render_core.py`.
- La compilacion PDF depende de LaTeX externo (`latexmk`/`xelatex`).
- Los mapas no se copian al repo por tamano; deben entregarse como insumo externo o con Git LFS.
- La inferencia de municipios en mapas/graficas depende de nombres de archivo con clave geo, clave de tres digitos o nombre normalizado del municipio.
