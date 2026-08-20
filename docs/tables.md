# Tablas

Referencia única para las tablas de los cuadernillos: estructura, alineaciones, encabezados, pies,
tamaños de fuente y colores.

Como referencia viva conviene mirar `templates/sections/geografia.tex.j2`, que tiene 21 tablas de
todas las formas posibles.

## Estructura base

Todas las tablas usan `longtable`. No se usa `table`, `tabular` ni `threeparttable`: solo `longtable`
puede partirse entre páginas, y varias tablas del cuadernillo lo hacen.

```latex
\setlength{\tabcolsep}{3pt}
\footnotesize
\begin{longtable}{>{\raggedright\arraybackslash}m{\dimexpr0.40\linewidth - 2\tabcolsep\relax}
                  >{\raggedleft\arraybackslash}m{\dimexpr0.30\linewidth - 2\tabcolsep\relax}
                  >{\raggedleft\arraybackslash}m{\dimexpr0.30\linewidth - 2\tabcolsep\relax}}

\caption{\textbf{Título de la tabla} \\
Nota preliminar opcional}
\label{tabla_nombre_descriptivo} \\

\hline
\rowcolor{gray!30}
\thh{0.40}{Col1}  &  \thhl{0.30}{Col2}  &  \thhl{0.30}{Col3} \\
\hline
\endfirsthead

\multicolumn{3}{l}{\small\textbf{(continuación)}} \\
\hline
\rowcolor{gray!30}
\thh{0.40}{Col1}  &  \thhl{0.30}{Col2}  &  \thhl{0.30}{Col3} \\
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
\tablefooter{Fuente: & IIEG, con base en INSTITUCIÓN. Producto consultado, 2025.}
```

El encabezado se escribe **dos veces**: en `\endfirsthead` para la primera página y en `\endhead`
para las siguientes. Si se cambia uno hay que cambiar el otro.

## Columnas

Se definen con proporciones de `\linewidth` que **sumen exactamente 1.00**, restando siempre
`2\tabcolsep`:

```latex
>{\raggedright\arraybackslash}m{\dimexpr0.40\linewidth - 2\tabcolsep\relax}
```

**Nunca se usan líneas verticales** (`|`), ni en la especificación de columnas ni en `\multicolumn`.

**Nunca se usa el macro `\ltcoleq{N}`** en `longtable`.

La alineación depende del contenido:

| Alineación | Comando | Cuándo |
|---|---|---|
| Izquierda | `\raggedright\arraybackslash` | Texto largo: nombres, descripciones, categorías |
| Derecha | `\raggedleft\arraybackslash` | Cifras, porcentajes, claves numéricas |
| Centrado | `\centering\arraybackslash` | Valores cualitativos: grados de marginación, intensidad migratoria |

## Encabezados

Las celdas de encabezado usan `\thh` (alineado a la izquierda) o `\thhl` (a la derecha), y reciben la
proporción de su columna:

```latex
\hline
\rowcolor{gray!30}
\thh{0.40}{Tipo de suelo}  &  \thhl{0.30}{Superficie (ha)}  &  \thhl{0.30}{Porcentaje} \\
\hline
```

**Todas las celdas de una fila de encabezado deben usar el mismo tipo de macro.** Mezclar `\thh` con
`\textbf{}` a secas deja los títulos a distinta altura: `\thh` envuelve su contenido en un `varwidth`
con espaciado propio, así que esa celda queda más alta y las demás se centran más abajo.

Para forzar un salto de línea dentro de un encabezado se usa `\newline`:

```latex
\thhl{0.21}{Variación (\%)\newline 2015--2020}
```

### `\multicolumn`

La especificación de columna **no lleva `|`**. El ancho de un `p{}` que abarca N columnas es la suma
de sus proporciones:

```latex
\multicolumn{2}{>{\centering\arraybackslash}m{\dimexpr0.24\linewidth - 2\tabcolsep\relax}}%
  {\cellcolor{gray!30}\textbf{Porcentaje}}
```

### `\makecell`

Cuando un `\multicolumn` usa `\makecell` para forzar un salto, la celda se vuelve más alta que sus
vecinas de una sola línea y deja un hueco visible. En una fila donde varias celdas `\multicolumn`
conviven, no se mezclan alturas: se da ancho suficiente para que el texto quepa en una línea, o se
usa `p{}` para que haga wrapping solo.

Nunca se escriben guiones manuales dentro de `\makecell`, como `\makecell{Pobla-\\ción}`. En columnas
`p{}` o `m{}` LaTeX hifena solo.

## Pie de tabla

Se usa el macro `\tablefooter`, que ya trae el espaciado negativo para quedar a ras de la tabla. No se
le antepone `\vspace`.

```latex
\tablefooter{Nota: & Texto de la nota.\\
ND: & No disponible.\\
Fuente: & IIEG, con base en INEGI. Producto consultado, 2025.}
```

El orden es **Nota → Llamada → Símbolos → Fuente**. La fuente es obligatoria; el resto es opcional.

Para cuadros elaborados por el IIEG con datos de otra fuente:

```latex
Fuente: & IIEG, con base en INSTITUCIÓN. Producto consultado, Año.
```

Con varias fuentes, cada una en su renglón:

```latex
\tablefooter{Fuente: IIEG, con base en & CONAGUA. Disponibilidad en cuencas hidrológicas, 2023.\\
 & CONAGUA. Ordenamiento de aguas superficial, 2023.}
```

### El pie es de dos columnas

`\tablefooter` renderiza dentro de un `tabularx` de **dos** columnas: la etiqueta y el texto. Un `&`
de más manda el resto a una fila nueva y parte la línea a la mitad.

```latex
ND: & No disponible.\\      % correcto
& ND: & No disponible.\\    % rompe: tres celdas
```

### Cuándo va la llamada `ND`

`ND: & No disponible.` solo se incluye **si la tabla contiene algún ND**. En las tablas cuyo contenido
depende de los datos, se condiciona:

```latex
<% if de_localidades_tiene_na %>ND: & No disponible.\\<% endif %>
```

Cuando el ND está escrito fijo en el template, porque el indicador no tiene ese dato por definición,
la llamada va sin condicional.

## Caption

El identificador del cuadro va en este orden, alineado a la izquierda:

1. **Número**, que genera LaTeX solo
2. **Título**, en negritas
3. **Nota preliminar**, opcional y sin negritas: normalmente el año o el periodo

```latex
\caption{\textbf{Geología de << ge_municipio >>} \\
<< ge_anio.geologia >>}
```

El año va en su propio renglón y **fuera** de las negritas.

### Color del caption

El formato `tablaformat` de `base.tex.j2` aplica `\color{colorTexto}` al caption. Es necesario:
`\caption` de LaTeX **no hereda** el color del documento y, sin eso, sale en negro puro mientras el
resto de los títulos van en gris.

## Tamaños de fuente

| Tamaño | Dónde |
|---|---|
| `\footnotesize` | Cuerpo de la tabla; se abre antes del `longtable` y se cierra con `\normalsize` |
| `\small` | Marcas de «(continuación)» y «(continúa)» |
| `\scriptsize` | Encabezados de tablas con muchas columnas, como las de economía |

El pie hereda `\footnotesize` del propio macro `\tablefooter`.

## Colores

Definidos en `templates/base.tex.j2`:

| Nombre | Hex | Uso |
|---|---|---|
| `gray!30` | (color de LaTeX) | Fondo de la fila de encabezado |
| `filaResaltada` | `#FFEACE` | Fila de agrupación dentro de la tabla |
| `rowHighlight` | `#FFF3CD` | Fila resaltada por condición, como el municipio propio |
| `colorTexto` | `#465055` | Texto y captions |
| `colorSeccion` | `#5C2472` | Títulos de sección y subsección |
| `headerGray` | `#7A7A7A` | Gris para encabezados secundarios |
| `lightGray` | `#D9D9D9` | Gris claro para separaciones |

En las tablas solo se usan `gray!30` para el encabezado y `filaResaltada` para las filas de
agrupación. Los demás existen para otros elementos del documento.

## Saltos de página antes de una tabla

Antes de una tabla grande se pone `\newpage`, para que no arranque al final de una página y quede
partida en dos.

Cuando conviene que la tabla quede en la misma página que su gráfica **siempre que quepa completa**,
existe `\tablafit`, definido en `templates/base.tex.j2`:

```latex
\tablafit{<número de filas>}
```

Va en lugar del `\newpage`. Mide el espacio que queda en la página y solo salta si la tabla no cabe;
si cabe, la deja a continuación. Se apoya en `\Needspace*` del paquete `needspace`.

El argumento es el número de filas del cuerpo, contando las de encabezado intermedias. El analizer lo
calcula y lo expone como una variable de contexto; el template solo la interpola.

Una `longtable` no se puede medir de antemano, así que la altura es una estimación: `7/5` de
`\baselineskip` por fila (altura real con `arraystretch` 1.5 en `\footnotesize`) más 6
`\baselineskip` de caption, encabezado, reglas y `\tablefooter`.

Al momento no se usa en ninguna tabla: se probó en cuencas y se prefirió el `\newpage`, porque con
125 cuadernillos la tabla quedaría abajo en unos municipios y en página aparte en otros, según
cuántas filas le tocaran. La consistencia entre cuadernillos pesa más que aprovechar el hueco.

## Valores no disponibles

Cuando un dato no existe se usa el macro `\ND`, que rinde `N/D` en rojo. Nunca se dejan celdas
vacías, guiones ni texto plano.

Para el «no disponible» tabular que va acompañado de su llamada al pie se usa la constante `DASH` de
`core/constants.py`, que rinde el literal `ND`.

## Formato de las cifras

Decimales, separador de miles, unidades y porcentajes siguen la NOM-008-SE-2021 y están documentados
aparte, en `.claude/rules/data-patterns.md`. En resumen:

- Dos decimales exactos en los valores; no en claves, años ni rankings
- Separador de miles con espacio fino: `1\,500`
- Unidad separada con espacio fino: `234\,km`, `35\,\%`
- El formateo se aplica en el analizer, no en el template
