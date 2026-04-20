Orquesta la construcción y revisión del pipeline para la sección $ARGUMENTS.

Usa el Agent tool para invocar los dos sub-agentes en secuencia. Espera a que el primero termine antes de lanzar el segundo.

## Paso 1 — Construcción

Invoca el sub-agente `pipeline-builder` con este prompt:

> Construye el pipeline para la sección $ARGUMENTS.

Espera el resultado. Si el sub-agente reporta errores de compilación que no pudo resolver, detente y repórtalos al usuario antes de continuar.

## Paso 2 — Revisión

Una vez que el builder termina exitosamente, invoca el sub-agente `pipeline-reviewer` con este prompt:

> Revisa el pipeline $ARGUMENTS. El PDF generado está en output/pdf/. Genera el reporte en output/review_$ARGUMENTS.md.

## Resumen final

Al terminar ambos sub-agentes, muestra:
- Estado del pipeline: ✅ compilado / ❌ error
- Ruta del PDF generado
- Resumen de hallazgos del revisor (de `output/review_$ARGUMENTS.md`)
- Acciones pendientes, si las hay
