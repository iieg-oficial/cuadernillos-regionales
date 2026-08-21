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
hi_   →  historia
ge_   →  geografia
de_   →  demografia
ec_   →  economia
gs_   →  gobierno_y_seguridad
dm_   →  directorio_municipal
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

### 4. Abre con la portada de sección

Las secciones no llevan `\section{}`: el nombre ya aparece en la portada. El template arranca con la
portada y ahí mismo se ancla la entrada del índice:

```latex
\clearpage
\thispagestyle{empty}
\phantomsection
\addcontentsline{toc}{section}{Nombre de la sección}
```

Dentro de la sección se usan `\subsection{}` y `\subsubsection{}` con normalidad.

---

## Variables

### Texto

Un valor estático en Overleaf:

```latex
\subsection{Acatic, Región Altos Sur}
```

Se convierte en:

```latex
\subsection{<< gs_municipio_nombre >>, << gs_region_nombre >>}
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

Las tablas tienen su propia referencia: **[docs/tables.md](tables.md)**, con la estructura de
`longtable`, alineaciones, encabezados, pies, caption, tamaños de fuente y colores.

Lo esencial: todas las tablas usan `longtable`, nunca `tabular` ni `table`, sin líneas verticales,
con columnas cuyas proporciones suman 1.00, encabezados con `\thh`/`\thhl` y pie con
`\tablefooter`.

Si tu `.tex` de Overleaf trae `\begin{tabular}{|c|l|c|}`, ahí está cómo convertirlo.

### Imágenes

#### Gráficas

Una imagen estática en Overleaf:

```latex
\includegraphics[width=\textwidth]{mi_grafica.png}
```

Se convierte en una figura con título numerado y pie:

```latex
\begin{figure}[H]
\graficatitulo{Título de la gráfica de << ge_municipio >>, << ge_anio.tema >>}
\centering
\includegraphics[width=\textwidth]{<< ge_tema_grafica >>}
\end{figure}
\tablefooter{<< ge_fuente.tema >>}
```

`\graficatitulo` lleva su propio contador, así que la numeración de gráficas es automática.

#### Mapas

Los mapas tienen su propia referencia: **[docs/maps.md](maps.md)**, con el origen de los archivos, la
resolución de nombres, la versión ligera, los límites de tamaño y el título.

Lo esencial: el mapa **no** se inserta con `\includegraphics` en el template. El analizer arma el
bloque completo y lo pasa como variable; el template solo pone el título y la variable:

```latex
\clearpage
\mapatitulo*{Título del mapa de << ge_municipio >>, << ge_anio_mapa.tema >>}
<< ge_tema_mapa >>
```

## Paquetes LaTeX disponibles

Los paquetes ya incluidos en `base.tex.j2`:

`adjustbox`, `array`, `babel`, `booktabs`, `caption`, `eso-pic`, `etoc`, `etoolbox`, `fancyhdr`,
`float`, `fontspec`, `footmisc`, `geometry`, `graphicx`, `hyperref`, `longtable`, `makecell`,
`multirow`, `setspace`, `siunitx`, `tabularx`, `threeparttable`, `tikz`, `titlesec`, `varwidth`,
`xcolor`, `xurl`

Si tu `.tex` de Overleaf usa algún paquete adicional, agrégalo en `base.tex.j2`.

## Macros propios

Definidos en `base.tex.j2`:

| Macro | Para qué sirve |
|---|---|
| `\ND` | Marca un dato no disponible |
| `\thh`, `\thhl` | Celda de encabezado de tabla, alineada a la izquierda o a la derecha |
| `\thdr`, `\thdl` | Celda de cuerpo resaltada |
| `\tablefooter` | Pie suelto de gráfica o mapa |
| `\tablefooterrow` | Pie de tabla, dentro de `\endlastfoot` |
| `\graficatitulo` | Título numerado de gráfica |
| `\mapatitulo` | Título numerado de mapa; la forma `*` lo guarda para `\mapabloque` |
| `\mapageo`, `\mapafijo` | Bloque de mapa: título y mapa alineados |
| `\mapafuente` | Pie de mapa con varias fuentes |
| `\versionnumero`, `\versionfecha` | Versión y fecha del cuadernillo |
| `\versioncuadernillo` | Las dos juntas, para el pie de página |

## Bitácora de versiones

`templates/bitacora.tex.j2` es la última página de contenido, antes de la contraportada. Lleva el
título `Bitácora de versiones` con `\subsection*` (morado, sin entrada en el índice, porque no
cuelga de ninguna sección) y una `longtable` de cuatro columnas: Versión, Fecha, Descripción del
cambio y Página.

Es la única tabla del cuadernillo **sin pie de fuente**: no hay fuente externa que citar, es un
registro interno del documento.

## Encabezado y pie de página

`base.tex.j2` define el `\pagestyle{fancy}` que llevan todas las páginas:

| Posición | Contenido |
|---|---|
| Encabezado izquierda | `logo_header.png` |
| Encabezado derecha | `Página \thepage` |
| Pie izquierda | `logo_footer.png` |
| Pie derecha | `\versioncuadernillo` |

`\versioncuadernillo` es la versión y fecha del cuadernillo (`v01 - 31/08/2026`), armada con
`\versionnumero` y `\versionfecha`. Las tres se definen en `base.tex.j2`, junto al `\pagestyle`, y
alimentan también el primer renglón de la bitácora de versiones.

Para publicar una versión nueva: cambiar `\versionnumero` y `\versionfecha`, y agregar el renglón que
corresponda en `templates/bitacora.tex.j2`.

Las portadas, las portadillas de sección y la contraportada usan `\thispagestyle{empty}`, así que no
llevan encabezado ni pie.

## Reglas de contenido

El formato de las cifras (decimales, separador de miles, unidades) y las reglas detalladas de tablas
están en `.claude/rules/data-patterns.md` y `.claude/rules/latex-templates.md`.
