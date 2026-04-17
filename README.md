# Cuadernillos Municipales

Genera un reporte PDF por municipio (125 en total) para Jalisco, México. Extrae datos de PostgreSQL, genera gráficas con matplotlib, renderiza templates Jinja2 LaTeX y compila con `pdflatex`.

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

Los templates usan la fuente Lexend. Descárgala e instálala antes de compilar:

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

Copia y ajusta la configuración general de la aplicación:

```bash
cp .env.example/.env.app.example .env/.env.app
```

Edita `.env/.env.app` con la ruta donde instalaste las fuentes:

```env
FONTS_PATH=/home/tu_usuario/.fonts/
```

## Uso

Ver [docs/just.md](docs/just.md) para la lista completa de comandos.

Los PDFs se generan en `output/pdf/{id}_cuadernillo/`.

## Documentación

- [Convención de commits](docs/commit-conventions.md)
- [Templates LaTeX](docs/latex-templates.md)
- [Comandos just](docs/just.md)
