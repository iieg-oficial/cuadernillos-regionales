# Cuadernillos Municipales

Los Cuadernillos Municipales son reportes estadísticos que el IIEG (Instituto de Información Estadística y Geográfica de Jalisco) publica para cada uno de los 125 municipios del estado. Cada cuadernillo concentra indicadores clave de historia, geografía, demografía, economía, gobierno y seguridad, y sirve como referencia oficial para la toma de decisiones en el ámbito municipal.

Este repositorio automatiza la generación de esos reportes: extrae datos de PostgreSQL, genera gráficas con matplotlib, renderiza templates Jinja2 LaTeX y compila con `xelatex`.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems/)
- [pre-commit](https://pre-commit.com/)
- TeX Live con `xelatex`
- Fuentes Lexend y Garet (ver [Fuentes](#fuentes))

## Instalación

Instala `just` siguiendo las instrucciones en [docs/just.md](docs/just.md), luego:

```bash
git clone git@github.com:iieg-oficial/cuadernillos.git
cd cuadernillos
just setup
```

### Fuentes

El proyecto usa dos familias tipográficas:

| Fuente | Dónde se usa | Cómo obtenerla |
|---|---|---|
| [Lexend](https://fonts.google.com/specimen/Lexend) | Todo el cuerpo del documento | Google Fonts |
| Garet | Portadas: general y de cada sección | Licencia del IIEG; pídela al equipo de diseño |

Ambas se cargan por ruta desde `FONTS_PATH`, no por nombre de sistema, así que basta con dejar los
archivos ahí. De Garet hacen falta los pesos **Extra Bold** y **Medium**:

```bash
cp Garet-Extra-Bold.otf Garet-Medium.otf ~/.fonts/
```

Los nombres de archivo están escritos en `templates/base.tex.j2`; si tu copia de Garet los nombra
distinto, ajústalos ahí.

#### Instalar Lexend

Descarga los pesos Light, Medium, SemiBold, Bold y ExtraBold:

```bash
# Descarga los archivos TTF desde Google Fonts
wget -O /tmp/lexend.zip "https://fonts.google.com/download?family=Lexend"
unzip /tmp/lexend.zip -d /tmp/lexend

# Copia los TTF a tu directorio de fuentes de usuario
mkdir -p ~/.fonts
cp /tmp/lexend/static/*.ttf ~/.fonts/

# Actualiza el caché de fuentes
fc-cache -fv
```

### Variables de entorno

Copia los archivos de ejemplo en `.env.example/` a `.env/` y llena las credenciales:

```bash
cp .env.example/.env.fiscalia.example .env/.env.fiscalia
# ... repite para cada base de datos
```

Cada base de datos tiene su propio archivo; ver [Bases de datos](docs/databases.md). Además de las credenciales, hay variables que configuran el documento:

| Archivo | Variable | Para qué sirve |
|---|---|---|
| `.env/.env.app` | `FONTS_PATH` | Ruta donde quedó instalada la fuente Lexend (por ejemplo `~/.fonts/`) |
| `.env/.env.app` | `ESCUDOS_URL` | ZIP de Drive con los escudos municipales |
| `.env/.env.demografia` | `DEMOGRAFIA_MAPS_*_URL` | Carpetas de Drive con los mapas de demografía |
| `.env/.env.geografia` | `GEOGRAFIA_MAPS_FOLDER_URL` | Carpeta de Drive con los mapas de geografía |

### Recursos que se descargan solos

En la primera corrida el pipeline descarga desde Google Drive lo que falte, y no vuelve a hacerlo si ya está en disco:

| Recurso | Destino |
|---|---|
| Escudos municipales | `assets/escudos_mun_jal/` |
| Mapas de demografía | `assets/maps/demografia/` |
| Mapas de geografía | `assets/maps/geografia/` |

Los tres directorios están en `.gitignore`: son insumos, no código.

## Uso

Ver [docs/just.md](docs/just.md) para la lista completa de comandos.

Hay dos modos de generación:

| Modo | Comando | Salida | xelatex |
|---|---|---|---|
| Desarrollo | `just run`, `just run-one <clave>` | `output/pdf/{clave}_{nombre}_cuadernillo_municipal_2026/` | una pasada |
| Final | `just run-prod [clave]`, `just run-prod-range <desde> <hasta>`, `just run-prod-one <clave>` | `output/pdf/prod/` y `output/tex/prod/` | dos pasadas |

El modo de desarrollo corre xelatex una sola vez y deja los archivos auxiliares junto al PDF: es más
rápido para iterar, pero el índice y las referencias cruzadas quedan sin resolver en una corrida
limpia. El modo final hace las dos pasadas que LaTeX necesita y escribe los auxiliares en un
directorio temporal, de modo que en `output/pdf/prod/` solo quedan los PDFs.

En desarrollo cada cuadernillo deja su `.tex` en su propia carpeta bajo `output/tex/`; en modo final
todos quedan planos en `output/tex/prod/`, sin archivos auxiliares.

El nombre del archivo se arma con la clave y el municipio sin acentos y en minúsculas
(`27_cuautitlan_de_garcia_barragan_cuadernillo_municipal_2026`), para que sea ASCII puro y no dé
problemas al moverlo entre sistemas.

Los `.tex` no son portables por sí solos: referencian mapas, gráficas y escudos por ruta relativa a la raíz del repositorio, y las fuentes por ruta absoluta.

## Documentación

- [Convención de commits](docs/commit-conventions.md)
- [Templates LaTeX](docs/latex-templates.md)
- [Tablas](docs/tables.md)
- [Mapas](docs/maps.md)
- [Bases de datos](docs/databases.md)
- [Comandos just](docs/just.md)

Las reglas de estilo que aplican al contenido de los cuadernillos, formato de cifras y estructura de los templates, viven en `.claude/rules/`.
