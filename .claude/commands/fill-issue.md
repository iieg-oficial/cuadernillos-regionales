Crea o encuentra el issue de GitHub para el pipeline actual.

## Pasos

1. Detecta el nombre de la sección del contexto actual (rama, archivos recientes, conversación).

2. Busca issues abiertos relacionados:
   ```bash
   gh issue list --state open --search "{seccion}" --json number,title,url
   ```

3. Si ya existe un issue claro para esta sección, muéstralo y pregunta:
   "¿Es este el issue correcto? (#N — título)"
   - Si sí: termina, devuelve el número para uso en `/fill-pr`.
   - Si no: continúa a crear uno nuevo.

4. Si no existe, crea el issue:

```bash
gh issue create \
  --title "feat(pipeline): {seccion}" \
  --label "pipeline" \
  --body "$(cat <<'EOF'
## Nombre de la sección

- [ ] geografia
- [ ] gobierno_y_seguridad
- [ ] demografia
- [ ] historia
- [ ] Otro: {seccion}

## Fuentes de datos

- [ ] PostgreSQL
- [ ] CSV
- [ ] JSON
- [ ] Otro: ¿cuál? ___

## Observaciones

## Notas
EOF
)"
```

5. Muestra la URL del issue creado.
