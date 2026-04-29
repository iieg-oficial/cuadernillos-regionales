Crea o actualiza el Pull Request de GitHub para el pipeline actual y lo vincula al issue correspondiente.

## Pasos

1. Detecta el nombre de la sección del contexto actual (rama, archivos recientes, conversación).

2. Verifica que la rama actual no sea `main` ni `development`. Si lo es, detente y avisa al usuario.

3. Busca el issue asociado:
   ```bash
   gh issue list --state open --search "{seccion}" --json number,title,url
   ```
   - Si hay exactamente uno claro, úsalo.
   - Si hay varios, pregunta cuál es el correcto.
   - Si no hay ninguno, indica al usuario que primero ejecute `/fill-issue`.

4. Verifica si ya existe un PR para la rama actual:
   ```bash
   gh pr list --head "$(git branch --show-current)" --json number,title,url
   ```

5a. Si ya existe un PR, muéstralo y pregunta si desea actualizarlo o dejarlo como está.

5b. Si no existe, crea el PR apuntando a `development`:
   ```bash
   gh pr create \
     --base development \
     --title "feat(pipeline): {seccion}" \
     --body "$(cat <<'EOF'
   Closes #{issue_number}

   ## Descripción

   Pipeline completo para la sección **{seccion}** de los Cuadernillos Municipales.

   ## Cambios

   - `pipelines/seccion_{N}/` — extracción, análisis y pipeline
   - `templates/sections/seccion_{N}.tex.j2` — template LaTeX
   - `README.md` del pipeline

   ## Checklist

   - [ ] Pipeline compila sin errores (`just run-one <municipio_id>`)
   - [ ] PDF revisado contra referencia IIEG
   - [ ] Linting pasa (`just lint`)
   - [ ] README actualizado
   EOF
   )"
   ```

6. Muestra la URL del PR creado o encontrado.
