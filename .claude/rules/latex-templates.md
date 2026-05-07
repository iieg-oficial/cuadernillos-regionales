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
\begin{longtable}{>{\raggedright\arraybackslash}p{\dimexpr0.35\linewidth - 2\tabcolsep\relax}
                  >{\raggedleft\arraybackslash}p{\dimexpr0.40\linewidth - 2\tabcolsep\relax}
                  >{\centering\arraybackslash}p{\dimexpr0.25\linewidth - 2\tabcolsep\relax}}

\caption{\textbf{Título de la tabla} \\ Nota preliminar opcional}
\label{tabla_nombre_descriptivo} \\

% Encabezado primera página
\hline
\rowcolor{gray!30}
\textbf{Col1} & \textbf{Col2} & \textbf{Col3} \\
\hline
\endfirsthead

% Encabezado páginas siguientes
\multicolumn{3}{l}{\small\textbf{(continuación)}} \\
\hline
\rowcolor{gray!30}
\textbf{Col1} & \textbf{Col2} & \textbf{Col3} \\
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
Nota: texto de nota (opcional).\\
Fuente: INSTITUCIÓN. Producto consultado, Año.}
```

### Identificador de la tabla (caption)

El identificador sigue este orden, todos alineados a la izquierda con interlineado sencillo:

1. **Número de tabla** (`Tabla X`) — sin negritas, generado automáticamente por LaTeX
2. **Título** — en negritas, envuelto en `\textbf{}`
3. **Nota preliminar** — opcional, sin negritas (subtítulo como años cubiertos)

```latex
\caption{\textbf{Título de la tabla} \\ Nota preliminar opcional}
```

### Reglas de columnas en longtable

**Siempre usar columnas explícitas con `p{\dimexpr X\linewidth - 2\tabcolsep\relax}`.**

- NUNCA usar el macro `\ltcoleq{N}` en longtable.
- NUNCA usar líneas verticales (`|`) en las especificaciones de columna ni en `\multicolumn`.
- Las proporciones de todas las columnas deben sumar exactamente `1.00`.
- La alineación depende del contenido:
  - `\raggedright\arraybackslash` para texto largo (descripciones, nombres)
  - `\centering\arraybackslash` para claves/IDs y valores categóricos (grados, lugares)
  - `\raggedleft\arraybackslash` para cifras numéricas (porcentajes, conteos, índices)

Ejemplo con 3 columnas (proporciones: 0.35 + 0.40 + 0.25 = 1.00):

```latex
\begin{longtable}{>{\raggedright\arraybackslash}p{\dimexpr0.35\linewidth - 2\tabcolsep\relax}
                  >{\raggedleft\arraybackslash}p{\dimexpr0.40\linewidth - 2\tabcolsep\relax}
                  >{\centering\arraybackslash}p{\dimexpr0.25\linewidth - 2\tabcolsep\relax}}
```

### Encabezados de columna

La información del encabezado debe ir en negritas (`\textbf{}`). Usar `\rowcolor{gray!30}` para el fondo del encabezado.

```latex
\hline
\rowcolor{gray!30}
\textbf{Col1} & \textbf{Col2} & \textbf{Col3} \\
\hline
```

### `\multicolumn` sin líneas verticales

En `\multicolumn`, la especificación de columna NO lleva `|`. El ancho del `p{}` para un span de N columnas es:

```
WIDTH = (A + B + ...) × \linewidth - 2\tabcolsep
```

Ejemplo con span de 2 columnas (proporciones A=0.09, B=0.07):

```latex
\multicolumn{2}{>{\centering\arraybackslash}p{\dimexpr0.09\linewidth + 0.07\linewidth - 2\tabcolsep\relax}}{\cellcolor{gray!30}\textbf{Encabezado}}
```

### `\makecell` en encabezados multicolumna

Cuando un `\multicolumn{N}{...}{}` usa `\makecell` para forzar salto de línea, la celda se vuelve más alta que las celdas adyacentes de una sola línea, dejando espacio en blanco visible.

**Regla:** En encabezados de fila donde varias celdas `\multicolumn` comparten la misma fila, NO mezclar celdas de diferente altura. Dar ancho suficiente para que el texto quepa en una línea, o usar `p{}` para que el texto haga wrapping sin forzar salto manual.

### `\makecell` con guiones explícitos

NUNCA usar `\makecell{Pobla-\\ción}` con un guión literal. En columnas `p{}`, LaTeX aplica hifenación automática si la palabra no cabe.

### Pie de tabla

Todos los elementos del pie usan fuente menor (`\footnotesize`). El orden obligatorio es:

1. **Nota** (opcional)
2. **Llamada** (opcional)
3. **Símbolos aclaratorios** (opcional)
4. **Fuente** (obligatorio)

```latex
\par\vspace{-4pt}\parbox{\linewidth}{\footnotesize
Nota: texto de nota.\\
Fuente: INSTITUCIÓN. Producto consultado, Año.}
```

Para cuadros elaborados por el IIEG con datos de otra fuente:

```latex
Fuente: IIEG con base en INSTITUCIÓN. Producto consultado, Año.
```

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
- Las subsecciones usan `\subsection*{Nombre}` (sin numeración). El color morado (`colorSeccion`) está definido globalmente en `base.tex.j2` — no sobreescribir en los templates.
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
