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
\subsection{Acatic — Región Altos Sur}
```

Se convierte en:

```latex
\subsection{<< gs_municipio_nombre >> — << gs_region_nombre >>}
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

Todas las tablas del proyecto usan `longtable` — no `tabular` ni `table`. Si tu `.tex` de Overleaf usa
`\begin{tabular}`, cámbialo a `\begin{longtable}`.

Las columnas se definen con proporciones de `\linewidth` que sumen 1.00, restando siempre
`2\tabcolsep`. **No se usan líneas verticales** (`|`) en ninguna tabla.

En Overleaf:

```latex
\begin{tabular}{|c|l|c|c|}
```

En el template:

```latex
\begin{longtable}{>{\raggedright\arraybackslash}m{\dimexpr0.40\linewidth - 2\tabcolsep\relax}
                  >{\raggedleft\arraybackslash}m{\dimexpr0.30\linewidth - 2\tabcolsep\relax}
                  >{\raggedleft\arraybackslash}m{\dimexpr0.30\linewidth - 2\tabcolsep\relax}}
```

La alineación depende del contenido:

| Alineación | Comando | Cuándo usarla |
|---|---|---|
| Izquierda | `\raggedright\arraybackslash` | Texto largo: nombres, descripciones |
| Derecha | `\raggedleft\arraybackslash` | Cifras, porcentajes, claves numéricas |
| Centrado | `\centering\arraybackslash` | Valores cualitativos: grados, categorías |

#### Encabezados

Las celdas de encabezado usan los macros `\thh` (alineado a la izquierda) y `\thhl` (a la derecha),
que reciben la proporción de la columna. **Todas las celdas de una misma fila de encabezado deben usar
el mismo macro**: mezclarlos con `\textbf{}` a secas deja los títulos a distinta altura.

```latex
\hline
\rowcolor{gray!30}
\thh{0.40}{Tipo de suelo}  &  \thhl{0.30}{Superficie (ha)}  &  \thhl{0.30}{Porcentaje}  \\
\hline
```

#### Pie de tabla

El pie usa `\tablefooter`, que ya trae el espaciado para quedar a ras de la tabla. El orden es
Nota → Fuente, y cada renglón se separa con `\\`:

```latex
\tablefooter{Nota: & Texto de la nota.\\
Fuente: & IIEG, con base en INEGI. Producto consultado, 2025.}
```

Ese mismo macro se usa bajo las gráficas y los mapas, sin `\vspace` extra, para que todos los pies
queden igual de pegados a su contenido.

#### Filas

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

#### Valores faltantes

Cuando un dato no existe se usa el macro `\ND`, nunca una celda vacía ni un guión.

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

Los mapas no se insertan con `\includegraphics`: el analizer arma el bloque LaTeX completo y lo pasa
como variable. El template solo pone el título y la variable:

```latex
\clearpage
\mapatitulo[\mapbleed]{Título del mapa de << ge_municipio >>, << ge_anio_mapa.tema >>}
<< ge_tema_mapa >>
```

Dos longitudes de `base.tex.j2` gobiernan la geometría de todos los mapas:

| Longitud | Para qué sirve |
|---|---|
| `\mapbleed` | Cuánto se extiende el mapa más allá del margen de texto, por cada lado |
| `\mapheadroom` | Espacio que se le reserva al título sobre el mapa |

El bloque que genera el analizer limita el mapa por ancho **y** por alto. Eso importa porque la
proporción de los mapas varía por municipio: los alargados son más altos y, sin el límite de altura,
no caben en la página junto a su título y se brincan a la siguiente.

`\mapatitulo` encoge el título si no cabe en una línea, para que nunca robe altura al mapa.

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
| `\tablefooter` | Pie de tabla, gráfica o mapa |
| `\graficatitulo` | Título numerado de gráfica |
| `\mapatitulo` | Título numerado de mapa |
| `\mapafuente` | Pie de mapa con varias fuentes |

## Reglas de contenido

El formato de las cifras (decimales, separador de miles, unidades) y las reglas detalladas de tablas
están en `.claude/rules/data-patterns.md` y `.claude/rules/latex-templates.md`.
