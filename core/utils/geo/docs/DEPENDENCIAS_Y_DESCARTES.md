# Dependencias y descartes

## Scripts incluidos

- `run_compilacion.py`: orquestador portable.
- `scripts/generar_graficas.py`: etapa de graficas desde estadisticas locales.
- `scripts/graficas_core.py`: nucleo de graficas, sin dependencia geoespacial.
- `scripts/generar_variables_texto.py`: consolidacion y validacion de variables de texto.
- `scripts/generar_catalogo_mapas.py`: catalogo de mapas desde `mapas/`.
- `scripts/generar_catalogo_graficas.py`: catalogo de graficas desde `graficas/`.
- `scripts/catalogo_core.py`: inferencia de municipio y variables LaTeX desde archivos.
- `scripts/render_latex.py`: wrapper de render portable.
- `scripts/render_core.py`: construccion de contexto y render Jinja/LaTeX.
- `scripts/pipeline_common.py`: logging, normalizacion de claves y utilidades comunes.
- `config/settings.py`: rutas relativas y variables de entorno.

## Scripts descartados del proceso original

- `00_validar_entorno.py`: validaba PostGIS, rasters y dependencias del procesamiento pesado.
- `01_generar_estadisticas.py`: calcula estadisticas espaciales.
- `07_sync_estadisticas_postgis.py`: sincroniza/hidrata estadisticas con PostgreSQL.
- `run_pipeline.py`: orquestaba el flujo completo con etapas pesadas.
- `catalogo_common.py`: construia indice municipal desde PostGIS.
- `cuadernillos_postgis_config.py`: conexion y lectura PostGIS.
- `cuadernillos_funciones.py`: nucleo de estadisticas geoespaciales y raster.
- `cuadernillos_especiales.py`: rutinas geoespaciales especiales.
- `config/db_config.py`: configuracion y helpers PostgreSQL/PostGIS.
- `config/temas_config.json`: configuracion de calculo de estadisticas.
- `config/rutas_config.py`: contenia rutas absolutas del entorno original.

## Dependencias Python requeridas

- `pandas`: lectura y combinacion de CSV.
- `numpy`: soporte numerico para graficas.
- `matplotlib`: generacion de PNG.
- `jinja2`: render de plantillas LaTeX.

## Dependencias externas no Python

- `latexmk` y `xelatex` solo si se usa `--compile`.

## Dependencias eliminadas

- PostGIS/PostgreSQL.
- QGIS.
- GeoPandas/Shapely/Fiona.
- Rasterio/GDAL.
- Capas vectoriales originales.
- Rasters originales.
- Dumps de base de datos.

## Mejoras futuras recomendadas

- Publicar `datos_estadisticos/` y `mapas/` como artefactos versionados con checksum.
- Agregar prueba automatizada con un municipio fixture.
- Parametrizar lista de tablas obligatorias de `render_core.py`.
- Generar reporte de referencias LaTeX faltantes como etapa bloqueante opcional.
