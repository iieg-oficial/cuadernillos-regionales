# Reglas para templates LaTeX

## Tablas

Toda tabla sigue esta estructura base:

```latex
\begin{table}[H]
\label{tabla_nombre_descriptivo}
\centering
\caption{Título de la tabla}
\begin{threeparttable}
\setlength{\tabcolsep}{3pt}
\footnotesize
\begin{tabular}{|>{\centering\arraybackslash}m{Xcm} ... |}
\hline

% Subtítulo
\rowcolor{colorSeccion}
\multicolumn{N}{|c|}{\color{white}Texto del subtítulo} \\
\hline

% Encabezado de columnas
\rowcolor{gray!30}
Col1 & Col2 & ... \\
\hline

% Filas de datos
Valor & Valor & ... \\
\hline

\end{tabular}
\begin{tablenotes}
\small
\item Elaboración del IIEG, con datos de FUENTE, AÑO.
\end{tablenotes}
\end{threeparttable}
\end{table}
```

### Reglas de tablas

- Siempre usar `[H]` para fijar la posición.
- Siempre incluir `\label{}` con nombre en snake_case.
- Siempre envolver en `\begin{threeparttable}` para poder usar `\begin{tablenotes}`.
- Siempre usar `\setlength{\tabcolsep}{3pt}` y `\footnotesize` dentro del bloque.
- Definir columnas con `>{\centering\arraybackslash}m{Xcm}` para controlar ancho y alineación.
  - Usar `>{\raggedright\arraybackslash}m{Xcm}` para columnas de texto largo (etiquetas).
- La primera fila (subtítulo) siempre usa `\rowcolor{colorSeccion}` con texto `\color{white}`.
- Los encabezados de columnas usan `\rowcolor{gray!30}`.
- Las filas de totales, categorías o el municipio objetivo usan `\rowcolor{orange!20}`.
- Usar `\makecell{}` para encabezados con salto de línea.
- La fuente siempre va en `\begin{tablenotes}` con `\small`.
- Si la fuente no cabe en `tablenotes`, usar `\par\vspace{4pt}\parbox{\textwidth}{\footnotesize ...}` después del `\end{tabular}`, antes del `\end{table}`.

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
