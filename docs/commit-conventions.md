# Convención de commits

Este proyecto usa [Conventional Commits](https://www.conventionalcommits.org/). Los mensajes son validados automáticamente por el hook `commit-msg` al hacer commit.

## Reglas

- Los mensajes se escriben **en inglés**.
- El autor es siempre el usuario que commitea; no se agregan coautores.
- Nunca se añade `Co-Authored-By` al mensaje.

## Formato

```
type(scope): description
```

- **type**: obligatorio
- **scope**: opcional, en minúsculas con guiones o guiones bajos
- **description**: en minúsculas, sin punto final

## Tipos válidos

| Tipo        | Cuándo usarlo                                      |
| ----------- | -------------------------------------------------- |
| `feat`      | Nueva funcionalidad                                |
| `fix`       | Corrección de bug                                  |
| `update`    | Mejora a funcionalidad existente                   |
| `refactor`  | Cambio de código que no agrega ni corrige nada     |
| `chore`     | Mantenimiento, dependencias, configuración         |
| `docs`      | Cambios en documentación                           |
| `merge`     | Merge de ramas                                     |

## Ejemplos

```
feat(gobierno_y_seguridad): adds delitos table
fix(core): handles null cvegeo in aggregate
update(renderer): switch to custom jinja2 delimiters
refactor(gobierno_y_seguridad): move ranking logic to helpers
chore: update dependencies
docs: add latex templates guide
```

## Scopes sugeridos

Usa el nombre del módulo o sección como scope:

- `core`: infraestructura compartida
- `gobierno_y_seguridad`: sección de gobierno y seguridad
- `renderer`, `compiler`, `settings`: módulos específicos de core
