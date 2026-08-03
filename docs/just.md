# just

`just` es el task runner del proyecto. Agrupa los comandos de desarrollo más comunes.

## Instalación

Versión requerida: **1.46.0**

**Opción 1 — script oficial:**

```bash
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin --tag 1.46.0
```

Verifica que `~/.local/bin` esté en tu `PATH`. Si no, agrégalo a tu `~/.bashrc` o `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Opción 2 — snap:**

```bash
sudo snap install just --classic
```

## Comandos

### `just setup`

Instala las dependencias Python con `uv`, configura los git hooks de formato y convención de commits con `pre-commit`.

```bash
just setup
```

### `just run`

Genera los cuadernillos PDF de los 125 municipios de Jalisco. Los archivos quedan en `output/pdf/`.

```bash
just run
```

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
