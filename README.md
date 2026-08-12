# Cuadernillos Municipales

Los Cuadernillos Municipales son reportes estadísticos que el IIEG (Instituto de Información Estadística y Geográfica de Jalisco) publica para cada uno de los 125 municipios del estado. Cada cuadernillo concentra indicadores clave de historia, geografía, demografía, economía, gobierno y seguridad, y sirve como referencia oficial para la toma de decisiones en el ámbito municipal.

Este repositorio automatiza la generación de esos reportes: extrae datos de PostgreSQL, genera gráficas con matplotlib, renderiza templates Jinja2 LaTeX y compila con `xelatex`.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems/)
- [pre-commit](https://pre-commit.com/)
- TeX Live con `xelatex`
- Fuente [Lexend](https://fonts.google.com/specimen/Lexend)

## Instalación

Instala `just` siguiendo las instrucciones en [docs/just.md](docs/just.md), luego:

```bash
git clone git@github.com:iieg-oficial/cuadernillos.git
cd cuadernillos
just setup
```

### Fuente Lexend

Los templates usan la fuente Lexend, incluidos los pesos Light, Medium, SemiBold, Bold y ExtraBold. Descárgala e instálala antes de compilar:

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

Cada base de datos tiene su propio archivo. Además de las credenciales, hay variables que configuran el documento:

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
| Escudos municipales | `assets/escudos_mun_jal_png_con_fondo/` |
| Mapas de demografía | `assets/maps/demografia/` |
| Mapas de geografía | `assets/maps/geografia/` |

Los tres directorios están en `.gitignore`: son insumos, no código.

## Uso

Ver [docs/just.md](docs/just.md) para la lista completa de comandos.

Los PDFs se generan en `output/pdf/{clave}_{Nombre}_cuadernillo_2026/`, y los `.tex` intermedios en `output/tex/`.

## Documentación

- [Convención de commits](docs/commit-conventions.md)
- [Templates LaTeX](docs/latex-templates.md)
- [Comandos just](docs/just.md)

Las reglas de estilo que aplican al contenido de los cuadernillos —formato de cifras y estructura de los templates— viven en `.claude/rules/`.
