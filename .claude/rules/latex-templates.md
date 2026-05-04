# Reglas para templates LaTeX

## Referencia

Antes de crear o modificar cualquier template, revisar el pipeline de demografía como referencia de implementación completa:

- Template: `templates/sections/demografia.tex.j2`
- Pipeline: `pipelines/demografia/`

## Tablas

Todas las tablas usan `longtable`. No usar `table`/`tabular`/`threeparttable`. La estructura base es:

```latex
\setlength{\tabcolsep}{3pt}
\footnotesize
\begin{longtable}{|>{\centering\arraybackslash}p{\dimexpr0.25\linewidth - 2\tabcolsep\relax}
                  |>{\raggedright\arraybackslash}p{\dimexpr0.35\linewidth - 2\tabcolsep\relax}
                  |>{\centering\arraybackslash}p{\dimexpr0.40\linewidth - 2\tabcolsep\relax}|}

\caption{Título de la tabla}
\label{tabla_nombre_descriptivo} \\

% Encabezado primera página
\rowcolor{colorSeccion}
\multicolumn{3}{|c|}{\color{white}Subtítulo} \\
\hline
\rowcolor{gray!30}
Col1 & Col2 & Col3 \\
\hline
\endfirsthead

% Encabezado páginas siguientes
\multicolumn{3}{l}{\small\textbf{(continuación)}} \\
\rowcolor{colorSeccion}
\multicolumn{3}{|c|}{\color{white}Subtítulo} \\
\hline
\rowcolor{gray!30}
Col1 & Col2 & Col3 \\
\hline
\endhead

% Pie de página intermedia
\hline
\multicolumn{3}{r}{\small\textbf{(continúa)}} \\
\endfoot

% Pie de última página
\hline
\endlastfoot

Valor & Valor & Valor \\
\hline

\end{longtable}
\normalsize
\par\vspace{-4pt}\parbox{\linewidth}{\footnotesize
Elaboración del IIEG, con datos de FUENTE, AÑO.}
```

### Reglas de columnas en longtable

**Siempre usar columnas explícitas con `p{\dimexpr X\linewidth - 2\tabcolsep\relax}`.**

- NUNCA usar el macro `\ltcoleq{N}` en longtable: aunque el PDF se genera, longtable no dibuja las líneas verticales interiores cuando las columnas se definen mediante expansión de macros.
- Las proporciones de todas las columnas deben sumar exactamente `1.00`.
- La alineación depende del contenido: `\centering\arraybackslash` para números y claves, `\raggedright\arraybackslash` para texto largo, `\raggedleft\arraybackslash` para montos o valores con decimales alineados a la derecha.

Ejemplo con 3 columnas (proporciones: 0.25 + 0.35 + 0.40 = 1.00):

```latex
\begin{longtable}{|>{\centering\arraybackslash}p{\dimexpr0.25\linewidth - 2\tabcolsep\relax}
                  |>{\raggedright\arraybackslash}p{\dimexpr0.35\linewidth - 2\tabcolsep\relax}
                  |>{\centering\arraybackslash}p{\dimexpr0.40\linewidth - 2\tabcolsep\relax}|}
```

### `\makecell` en encabezados multicolumna

Cuando un `\multicolumn{N}{c|}{}` usa `\makecell` para forzar salto de línea, la celda se vuelve más alta que las celdas adyacentes de una sola línea, dejando espacio en blanco visible.

**Regla:** En encabezados de fila donde varias celdas `\multicolumn` comparten la misma fila, NO mezclar celdas de diferente altura. Opciones:

1. **Dar ancho suficiente** para que el texto quepa en una línea: ajustar las proporciones de las columnas que forman el span.
2. **Cambiar la alineación del multicolumn de `c` a `p{}`** para que el texto pueda hacer wrapping sin forzar salto manual:

```latex
% En lugar de:
\multicolumn{2}{c|}{\makecell{Intensidad\\Migratoria}}

% Usar:
\multicolumn{2}{>{\centering\arraybackslash}p{\dimexpr A\linewidth + B\linewidth - 2\tabcolsep + \arrayrulewidth\relax}|}{Intensidad Migratoria}
```

Donde A y B son las proporciones de las dos columnas que forma el span. La fórmula del ancho del `p{}` en el multicolumn es:

```
WIDTH = (A + B) × \linewidth - 2\tabcolsep + \arrayrulewidth
```

### `\makecell` con guiones explícitos

NUNCA usar `\makecell{Pobla-\\ción}` con un guión literal. En columnas `p{}`, LaTeX aplica hifenación automática si la palabra no cabe. Si la palabra cabe, no hace falta nada. Si la columna es muy estrecha y el resultado visual es incorrecto, ampliar la proporción de esa columna.

## Imágenes (mapas y gráficas)

Las imágenes se insertan como variables de contexto, no con rutas fijas en el template:

```latex
\newpage
<< nombre_variable_imagen >>
\newpage
```

El analizer genera el bloque LaTeX completo y lo pasa en la variable. El patrón del bloque generado es:

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{ruta/imagen.png}
\caption{Título de la imagen}
\end{figure}
```

## Valores no disponibles

Cuando un dato no existe o no aplica, usar el macro `\ND`:

```latex
\ND
```

Definido en `base.tex.j2` como `\textcolor{red}{N/D}`. Nunca usar celdas vacías, guiones ni texto plano para indicar ausencia de datos.

## Estructura de página

- Cada sección nueva abre con `\section{Nombre}`.
- Las subsecciones usan `\subsection{Nombre}` (sin numeración pero aparece en el índice). Las subsubsecciones usan `\subsubsection*{Nombre}` (sin numeración y sin aparecer en el índice). El color morado (`colorSeccion`) está definido globalmente en `base.tex.j2` — no sobreescribir en los templates.
- Antes de tablas grandes o imágenes, agregar `\newpage` para evitar cortes.
- Las portadas de sección usan `\clearpage`, `\thispagestyle{empty}` y `\AddToShipoutPictureBG*` con la imagen de fondo `portada.png`.

## Colores disponibles

Definidos en `base.tex.j2`:

| Nombre         | Hex       | Uso                                         |
|----------------|-----------|---------------------------------------------|
| `colorSeccion` | `#5C2472` | Subtítulo de tabla, encabezados de sección  |
| `colorTexto`   | `#465055` | Texto principal                             |
| `headerBg`     | `#5C2472` | Fondo de encabezado (igual que colorSeccion)|
| `subheaderBg`  | `#7A4A8A` | Fondo de subencabezado                      |
| `rowHighlight` | `#FFF3CD` | Fila resaltada condicionalmente             |
| `headerGray`   | `#7A7A7A` | Gris para encabezados secundarios           |
| `lightGray`    | `#D9D9D9` | Gris claro para separaciones               |
