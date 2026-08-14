# Reglas para templates LaTeX

## Referencia

Antes de crear o modificar cualquier template, revisar el pipeline de demografía como referencia de implementación completa:

- Template: `templates/sections/demografia.tex.j2`
- Pipeline: `pipelines/demografia/`

## Tablas

Ver [docs/tables.md](../../docs/tables.md). Ahí está todo: estructura de `longtable`, proporciones y
alineaciones de columna, encabezados con `\thh`/`\thhl`, `\multicolumn`, `\makecell`, caption,
pie con `\tablefooter`, tamaños de fuente y colores.

Reglas que no se negocian:

- Solo `longtable`; nunca `table`, `tabular` ni `threeparttable`
- Sin líneas verticales (`|`) en ningún lado
- Las proporciones de columna suman exactamente 1.00
- Cifras a la derecha, texto a la izquierda, valores cualitativos al centro
- Todas las celdas de una fila de encabezado usan el mismo macro
- El pie es de dos columnas: un `&` de más parte la línea
- Orden del pie: Nota → Llamada → Símbolos → Fuente

## Imágenes (mapas y gráficas)

Los mapas tienen su propia referencia: [docs/maps.md](../../docs/maps.md).

Las gráficas se insertan como figura con título numerado y pie:

```latex
\begin{figure}[H]
\graficatitulo{Título de la gráfica de << ge_municipio >>, << ge_anio.tema >>}
\centering
\includegraphics[width=\textwidth]{<< ge_tema_grafica >>}
\end{figure}
\tablefooter{<< ge_fuente.tema >>}
```

Los mapas NO usan `\includegraphics`: el analizer arma el bloque y lo pasa como variable.

```latex
\clearpage
\mapatitulo[\mapbleed]{Título del mapa de << ge_municipio >>, << ge_anio_mapa.tema >>}
<< ge_tema_mapa >>
```

Los pies de gráfica y de mapa usan `\tablefooter`, sin `\vspace` extra, para quedar a ras de la
imagen.

## Valores no disponibles

Cuando un dato no existe o no aplica, usar el macro `\ND`:

```latex
\ND
```

Definido en `base.tex.j2` como `\textcolor{red}{N/D}`. Nunca usar celdas vacías, guiones ni texto plano para indicar ausencia de datos.

## Estructura de página

- Las secciones NO usan `\section{}`: el nombre ya aparece en la portada de sección, que ancla su
  propia entrada del índice con `\phantomsection` + `\addcontentsline`.
- Las subsecciones usan `\subsection{Nombre}` (sin numeración pero aparece en el índice). Las subsubsecciones usan `\subsubsection*{Nombre}` (sin numeración y sin aparecer en el índice). El color morado (`colorSeccion`) está definido globalmente en `base.tex.j2`; no sobreescribir en los templates.
- Antes de tablas grandes o imágenes, agregar `\newpage` para evitar cortes.
- Las portadas de sección usan `\clearpage`, `\thispagestyle{empty}` y `\AddToShipoutPictureBG*` con
  las imágenes `portadilla.png` y `footer_section.png`.

## Colores disponibles

Ver [docs/tables.md](../../docs/tables.md#colores).
