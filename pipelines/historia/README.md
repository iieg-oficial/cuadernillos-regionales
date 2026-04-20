# Historia

Cubre la toponimia y el contexto histórico del municipio, acompañados de un mapa de localización geográfica dentro del estado de Jalisco.

## Fuentes de datos

| Fuente | Descripción | Variables principales |
|---|---|---|
| PDFs del IIEG (`iieg.gob.mx`) | Documentos PDF por municipio descargados desde el índice en línea del IIEG; el texto se extrae con `pdftotext` | `toponimia`, `contexto_historico` |
| Google Drive (carpeta de mapas) | Imágenes PNG de localización geográfica descargadas vía `gdown` desde la URL configurada en `.env.historia` | `mapa_path` |
| `assets/catalogs/regions.json` | Catálogo local con IDs y nombres de municipios | `municipio_nombre` |

## Notas

- El catálogo de textos se genera una sola vez y se guarda en `assets/catalogs/historia.json`. En ejecuciones posteriores se lee directamente del archivo sin volver a descargar los PDFs.
- Los mapas se descargan automáticamente una sola vez a `assets/maps/historia/`. Si la carpeta existe y tiene contenido, no se vuelven a descargar.
- El nombre del archivo de mapa esperado sigue el patrón `ubicacion_14{municipio_id}.png` (ID de tres dígitos con cero a la izquierda).
- Si no se encuentra el mapa del municipio, se usa `templates/assets/mapa_placeholder.png` como fallback.
- La URL de Google Drive para los mapas se configura en `.env/.env.historia` con la variable `HISTORIA_MAPS_URL`. Sin este valor, la descarga de mapas no funciona.
- La verificación SSL está deshabilitada en las peticiones HTTP al sitio del IIEG (`CERT_NONE`), decisión tomada por problemas de certificado en el servidor de origen.
- La extracción de texto de los PDFs depende de que exista el binario `pdftotext` en el sistema (paquete `poppler-utils`).
