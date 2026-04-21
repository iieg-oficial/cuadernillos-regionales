Orquesta la construcción y revisión del pipeline para la sección $ARGUMENTS.

El formato de invocación es: `/pipeline <nombre_seccion> [instrucciones adicionales]`

El nombre de la sección es la primera palabra de $ARGUMENTS (e.g. `historia`, `demografia`, `geografia`).
Las instrucciones adicionales (todo lo que sigue) describen requisitos especiales del pipeline.

Usa el Agent tool para invocar los dos sub-agentes en secuencia. Espera a que el primero termine antes de lanzar el segundo.

## Paso 1 — Construcción

Invoca el sub-agente `pipeline-builder` pasándole:
- El nombre de la sección (primera palabra de $ARGUMENTS)
- Las instrucciones adicionales que el usuario haya dado

Espera el resultado. Si reporta errores de compilación irresolubles, detente y repórtalos al usuario.

## Paso 2 — Revisión

Una vez que el builder termina exitosamente, invoca el sub-agente `pipeline-reviewer` con:
- El nombre de la sección
- La ruta del PDF generado en `output/pdf/`
- Instrucción de generar el reporte en `output/review_<nombre_seccion>.md`

## Resumen final

Al terminar ambos sub-agentes, muestra:
- Estado del pipeline: ✅ compilado / ❌ error
- Ruta del PDF generado
- Resumen de hallazgos del revisor (de `output/review_<nombre_seccion>.md`)
- Acciones pendientes, si las hay
