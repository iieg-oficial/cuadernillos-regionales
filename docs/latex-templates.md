# De Overleaf a template

Esta guía explica cómo convertir un archivo `.tex` de Overleaf en un template Jinja2 para el proyecto.

## Por qué delimitadores personalizados

Jinja2 usa `{{ }}` y `{% %}` por defecto, pero LaTeX también usa `{}` extensivamente. Para evitar conflictos, el renderer usa delimitadores distintos:

| Propósito   | Apertura | Cierre |
| ----------- | -------- | ------ |
| Variables   | `<<`     | `>>`   |
| Bloques     | `<%`     | `%>`   |
| Comentarios | `<#`     | `#>`   |

## Convención de variables

Todas las variables del template deben llevar un prefijo con las iniciales de la sección, seguido de guión bajo. Esto evita colisiones entre secciones cuando se fusionan los contextos.

```
gs_   →  gobierno_y_seguridad
de_   →  demografia
ec_   →  economia
```

**Correcto:**

```latex
<< gs_municipio_nombre >>
<< gs_region_nombre >>
<< gs_tabla_delitos >>
```

**Incorrecto:**

```latex
<< municipio_nombre >>
<< tabla_delitos >>
```

## Pasos

### 1. Crea el archivo del template

Crea `templates/sections/nombre_seccion.tex.j2` y pega el contenido de tu `.tex` de Overleaf.

### 2. Identifica los valores dinámicos

Busca todo lo que cambia por municipio: nombre, región, valores de tablas, rutas de imágenes, etc. Esos valores estáticos se reemplazan con variables usando `<< >>`.

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
\section{<< gs_municipio_nombre >> — << gs_region_nombre >>}
```

Un valor numérico dentro de texto:

```latex
En 2024 se registraron 42 delitos de fuero común.
```

Se convierte en:

```latex
En << gs_anio_actual >> se registraron << gs_total_delitos >> delitos de fuero común.
```

### Tablas

Todas las tablas del proyecto usan `longtable`. No usar `table`, `tabular` ni `threeparttable`.

La estructura base de toda tabla es:

```latex
\setlength{\tabcolsep}{3pt}
\footnotesize
\begin{longtable}{|>{\centering\arraybackslash}p{\dimexpr0.30\linewidth - 2\tabcolsep\relax}
                  |>{\raggedright\arraybackslash}p{\dimexpr0.40\linewidth - 2\tabcolsep\relax}
                  |>{\centering\arraybackslash}p{\dimexpr0.30\linewidth - 2\tabcolsep\relax}|}

\caption{Título de la tabla}
\label{tabla_nombre_descriptivo} \\

\rowcolor{colorSeccion}
\multicolumn{3}{|c|}{\color{white}<< gs_municipio_nombre >>} \\
\hline
\rowcolor{gray!30}
Col1 & Col2 & Col3 \\
\hline
\endfirsthead

\multicolumn{3}{l}{\small\textbf{(continuación)}} \\
\rowcolor{colorSeccion}
\multicolumn{3}{|c|}{\color{white}<< gs_municipio_nombre >>} \\
\hline
\rowcolor{gray!30}
Col1 & Col2 & Col3 \\
\hline
\endhead

\hline
\multicolumn{3}{r}{\small\textbf{(continúa)}} \\
\endfoot

\hline
\endlastfoot

Valor & Valor & Valor \\
\hline

\end{longtable}
\normalsize
\par\vspace{-4pt}\parbox{\linewidth}{\footnotesize
Elaboración del IIEG, con datos de FUENTE, AÑO.}
```

**Reglas de columnas:**

- Las proporciones de todas las columnas deben sumar exactamente `1.00`.
- Siempre restar `2\tabcolsep`: `p{\dimexpr0.30\linewidth - 2\tabcolsep\relax}`.
- Usar `\raggedright\arraybackslash` para columnas de texto (nombres, etiquetas). Usar `\centering\arraybackslash` para columnas numéricas.
- **Nunca usar macros como `\ltcoleq{N}`** en la especificación de columnas de longtable: aunque el PDF se genera, las líneas verticales interiores no se dibujan.

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
<< row.clave >> & << row.municipio >> & << row.valor >> & << row.lugar >> \\
\hline
<% endfor %>
```

Para resaltar una fila con condición:

```latex
<% for row in gs_tabla_delitos %>
<% if row.es_objetivo %>\rowcolor{rowHighlight}<% endif %>
<< row.clave >> & << row.municipio >> & << row.valor >> & << row.lugar >> \\
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
\includegraphics[width=\textwidth]{<< gs_grafica_delitos >>}
```

Donde `gs_grafica_delitos` es la ruta absoluta o relativa a la imagen generada, por ejemplo `output/charts/1_cuadernillo/delitos.png`.

---

## Paquetes LaTeX disponibles

Los paquetes ya incluidos en `base.tex.j2`:

`fontspec`, `xcolor`, `graphicx`, `float`, `geometry`, `fancyhdr`, `setspace`, `siunitx`, `tikz`, `eso-pic`, `babel`, `adjustbox`, `array`, `makecell`, `booktabs`, `multirow`, `hyperref`, `etoc`, `varwidth`, `tabularx`, `longtable`, `caption`

Si tu `.tex` de Overleaf usa algún paquete adicional, agrégalo en `base.tex.j2`.
