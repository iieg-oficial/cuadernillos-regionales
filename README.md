# Cuadernillos Municipales

Genera un reporte PDF por municipio (125 en total) para Jalisco, México. Extrae datos de PostgreSQL, genera gráficas con matplotlib, renderiza templates Jinja2 LaTeX y compila con `pdflatex`.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems/)
- [pre-commit](https://pre-commit.com/)
- TeX Live con `pdflatex`

## Instalación

```bash
git clone git@github.com:iieg-oficial/cuadernillos.git
cd cuadernillos
just setup
```

Copia los archivos de ejemplo en `.env.example/` a `.env/` y llena las credenciales:

```bash
cp .env.example/.env.fiscalia.example .env/.env.fiscalia
```

## Uso

```bash
just run            # genera todos los municipios
just run-one 1      # genera un municipio específico
just lint           # revisa estilo de código
just fix            # corrige estilo automáticamente
```

Los PDFs se generan en `output/pdf/{id}_cuadernillo/`.

## Documentación

- [Convención de commits](docs/commit-conventions.md)
- [Templates LaTeX](docs/latex-templates.md)
