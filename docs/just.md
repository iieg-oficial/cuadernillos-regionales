# just

`just` es el task runner del proyecto. Agrupa los comandos de desarrollo más comunes.

## Instalación

Versión requerida: **1.46.0**

**Opción 1, script oficial:**

```bash
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin --tag 1.46.0
```

Verifica que `~/.local/bin` esté en tu `PATH`. Si no, agrégalo a tu `~/.bashrc` o `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Opción 2, snap:**

```bash
sudo snap install just --classic
```

## Comandos

Las recetas están agrupadas en tres grupos: `setup` para preparar el entorno, `dev` para iterar
durante el desarrollo y `prod` para generar los cuadernillos finales.

## Preparación

### `just setup`

Instala las dependencias Python con `uv`, configura los git hooks de formato y convención de commits con `pre-commit`.

```bash
just setup
```

## Desarrollo

Una sola pasada de xelatex, salida en `output/pdf/{clave}_{nombre}_cuadernillo_municipal_2026/` junto
con los archivos auxiliares de LaTeX. Es el modo rápido para iterar; en una corrida limpia el índice
sale vacío y las referencias cruzadas sin resolver.

### `just run`

Genera los cuadernillos PDF de los 125 municipios de Jalisco, en orden de clave. Cada uno queda en su
propia carpeta bajo `output/pdf/`, junto con los archivos auxiliares de LaTeX.

Corre xelatex una sola vez: es el modo rápido para iterar. En una corrida limpia el índice sale vacío
y las referencias cruzadas sin resolver; para la versión final usa `just prod-run`.

```bash
just run
```

En la primera corrida descarga desde Google Drive los escudos municipales y los mapas que falten. Si
ya están en disco no vuelve a descargarlos.

De cada mapa se guarda una versión ligera en `output/maps/`, que se reutiliza entre corridas. Se
regenera sola cuando el original es más reciente, así que al recibir mapas nuevos no hace falta
borrar nada a mano.

### `just run-one <clave>`

Genera el cuadernillo de un solo municipio, identificado por su clave. Útil durante el desarrollo para probar sin procesar todos los municipios.

```bash
just run-one 1
```

### `just run-sample`

Genera los cuadernillos de una muestra representativa de municipios (metropolitanos, costa, sierra, altos y municipios pequeños). Útil para probar cambios sin correr los 125 municipios completos.

```bash
just run-sample
```

### `just open-one <clave>`

Abre el pdf específico del municipio.

```bash
just open-one 1
```

## Producción

Dos pasadas de xelatex, que es lo que LaTeX necesita para resolver el índice y las referencias. Los
PDFs quedan planos en `output/pdf/prod/` y los `.tex` en `output/tex/prod/`, sin archivos auxiliares:
se escriben en un directorio temporal que se descarta al terminar.

### `just prod-run [clave]`

Genera los cuadernillos finales de los 125 municipios en `output/pdf/prod/`, todos en la misma
carpeta y sin archivos auxiliares. Los `.tex` quedan igual de planos en `output/tex/prod/`.

```bash
just prod-run
```

A diferencia de `just run`, corre xelatex **dos veces** por cuadernillo, que es lo que LaTeX necesita
para resolver el índice y las referencias cruzadas. Los archivos auxiliares se escriben en un
directorio temporal que se descarta al terminar.

Acepta una clave opcional para reanudar el lote desde ese municipio, en orden de clave, útil si se
interrumpió a la mitad:

```bash
just prod-run 39   # procesa del 39 al 125
```

### `just prod-run-range <desde> <hasta>`

Genera un rango de cuadernillos finales por clave, con ambos extremos incluidos.

```bash
just prod-run-range 5 8   # procesa 5, 6, 7 y 8
```

Valida las dos claves antes de arrancar: si alguna no está en el catálogo, o si el rango queda
invertido, corta de inmediato en vez de fallar a media corrida.

### `just prod-run-one <clave>`

Genera un solo cuadernillo final en `output/pdf/prod/`. Útil para revisar un municipio con el índice
y las referencias ya resueltas antes de lanzar el lote completo.

```bash
just prod-run-one 39
```

### `just prod-open-one <clave>`

Abre el cuadernillo final de un municipio desde `output/pdf/prod/`.

```bash
just prod-open-one 39
```

## Calidad

### `just lint`

Revisa el estilo y formato del código con `ruff` sin modificar ningún archivo. Equivalente a correr el pre-commit manualmente.

```bash
just lint
```

### `just fix`

Corrige automáticamente los errores de estilo y formato detectados por `ruff`.

```bash
just fix
```

### `just test`

Ejecuta la suite de pruebas con `pytest`.

```bash
just test
```
