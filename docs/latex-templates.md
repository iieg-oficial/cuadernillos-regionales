# De Overleaf a template

Esta guía explica cómo convertir un archivo `.tex` de Overleaf en un template Jinja2 para el proyecto.

## Por qué delimitadores personalizados

Jinja2 usa `{{ }}` y `{% %}` por defecto, pero LaTeX también usa `{}` extensivamente. Para evitar conflictos, el renderer usa delimitadores distintos:

| Propósito   | Apertura              | Cierre                |
| ----------- | --------------------- | --------------------- |
| Variables   | `\verb` `<<\|`        | `>>\|`             |
| Bloques     | `\verb` `<%\|`        | `%>`                  |
| Comentarios | `\verb` `<#\|`        | `#>`                  |## Convención de variables

Todas las variables del template deben llevar un prefijo con las iniciales de la sección, seguido de guión bajo. Esto evita colisiones entre secciones cuando se fusionan los contextos.

```
gs_   →  gobierno_y_seguridad
de_   →  demografia
ec_   →  economia
```

**Correcto:**

```latex
\verb|<< gs_municipio_nombre >>|
\verb|<< gs_region_nombre >>|
\verb|<< gs_tabla_delitos >>|
```

**Incorrecto:**

```latex
\verb|<< municipio_nombre >>|
\verb|<< tabla_delitos >>|
```

## Pasos

### 1. Crea el archivo del template

Crea `templates/sections/nombre_seccion.tex.j2` y pega el contenido de tu `.tex` de Overleaf.

### 2. Identifica los valores dinámicos

Busca todo lo que cambia por municipio: nombre, región, valores de tablas, rutas de imágenes, etc. Esos valores estáticos se reemplazan con variables usando `\verb|<< >>|
`.

### 3. Registra el template en `reporte.tex.j2`

Agrega una línea `include` al final de `reporte.tex.j2`:

```latex
<% include "sections/nombre_seccion.tex.j2" %>
```

---

## Variables

### Texto

Un valor estático en Overleaf:

```latex
\section{Acatic — Región Altos Sur}
```

Se convierte en:

```latex
\section{\verb|<< gs_municipio_nombre >>| — \verb|<< gs_region_nombre >>|}
```

Un valor numérico dentro de texto:

```latex
En 2024 se registraron 42 delitos de fuero común.
```

Se convierte en:

```latex
En \verb|<< gs_anio_actual >>| se registraron << gs_total_delitos >> delitos de fuero común.
```

### Tablas

Las filas estáticas en Overleaf:

```latex
117 & Cañadas de Obregón & 7  & 14 \\
\hline
48  & Jesús María         & 29 & 51 \\
\hline
```

Se convierten en un loop:

```latex
<% for row in gs_tabla_delitos %>
 row.clave &  row.municipio  & row.anio\_censo  & row.poblacion\_total \\
\hline
<% endfor %>
```

Para resaltar una fila con condición:

```latex
<% for row in gs_tabla_delitos %>
<% if row.es_objetivo %>\rowcolor{rowHighlight}<% endif %>
row.clave &  row.municipio  & row.anio\_censo  & row.poblacion\_total \\ \\
\hline
<% endfor %>
```

### Imágenes

Una imagen estática en Overleaf:

```latex
\includegraphics[width=\textwidth]{mi_grafica.png}
```

Se convierte en:

```latex
\includegraphics[width=\textwidth]{\verb|<< gs_grafica_delitos >>|}
```

Donde `gs_grafica_delitos` es la ruta absoluta o relativa a la imagen generada, por ejemplo `output/charts/1_cuadernillo/delitos.png`.

---

## Paquetes LaTeX disponibles

Los paquetes ya incluidos en `base.tex.j2`:

`inputenc`, `fontenc`, `babel`, `geometry`, `lmodern`, `xcolor`, `graphicx`, `float`, `booktabs`, `tabularx`, `multirow`, `makecell`, `colortbl`, `array`, `fancyhdr`, `hyperref`

Si tu `.tex` de Overleaf usa algún paquete adicional, agrégalo en `base.tex.j2`.
