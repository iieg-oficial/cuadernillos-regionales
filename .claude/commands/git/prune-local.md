Elimina ramas locales cuyo branch remoto ya no existe.

Argumentos recibidos: $ARGUMENTS

- Sin argumentos: lista las ramas huérfanas y pide confirmación antes de borrar.
- `--dry-run`: solo lista las ramas, no borra nada.
- `--force`: borra sin pedir confirmación.

## Pasos

1. Actualiza las referencias remotas:

```bash
git fetch --prune
```

2. Lista las ramas locales cuyo remoto aparece como `gone`:

```bash
git branch -vv | grep ': gone]'
```

Si no hay ninguna, informa "No hay ramas locales huérfanas" y termina.

3. Muestra la lista de ramas encontradas:

```
Ramas huérfanas (su remoto ya no existe):
  - nombre-rama-1
  - nombre-rama-2
```

4. Según el argumento recibido:

- **`--dry-run`**: termina aquí, no borrar nada.
- **`--force`**: borra directamente sin pedir confirmación.
- **Sin argumentos**: pregunta "¿Eliminar estas ramas? (s/N)" y espera respuesta antes de continuar.

5. Para cada rama a eliminar:

```bash
git branch -d <nombre-rama>
```

Si `-d` falla porque la rama no está mergeada, repórtala y pregunta si se desea forzar con `-D`. No usar `-D` sin confirmación explícita, incluso con `--force`.

6. Reporta el resultado: cuántas ramas se eliminaron y cuáles quedan localmente.
