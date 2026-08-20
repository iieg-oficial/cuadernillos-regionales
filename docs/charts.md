# Gráficas

Referencia única para las gráficas de los cuadernillos: cómo se insertan, el título numerado y el
pie.

Las gráficas sí se insertan con `\includegraphics`, a diferencia de los mapas. Ver
[Mapas](maps.md) para el caso contrario.

## Estructura

```latex
\begin{figure}[H]
\graficatitulo{Título de la gráfica de << ge_municipio >>, << ge_anio.tema >>}
\centering
\includegraphics[width=\textwidth]{<< ge_tema_grafica >>}
\end{figure}
\tablefooter{Fuente: & INSTITUCIÓN. Producto consultado, Año.}
```

`\graficatitulo` lleva su propio contador: numera la gráfica y rinde «Gráfica N» sobre el título en
negritas. No se escribe el número a mano.

Las secciones que arman el bloque desde el analizer (economía) emiten el mismo LaTeX como cadena y lo
pasan como variable de contexto; el template solo interpola la variable.

## Pie de gráfica

El pie usa **`\tablefooter`**, el mismo macro que las tablas. No se usa un bloque
`\footnotesize` suelto ni se le antepone `\vspace`: el macro ya trae su espaciado negativo para
quedar a ras de la imagen.

```latex
\tablefooter{Nota: & Texto de la nota.\\
Fuente: & IIEG, con base en INSTITUCIÓN. Producto consultado, Año.}
```

El orden es **Nota → Fuente**, igual que en las tablas. La fuente es obligatoria; la nota es
opcional.

### Es de dos columnas

`\tablefooter` renderiza dentro de un `tabularx` de **dos** columnas: la etiqueta y el texto. Eso es
lo que alinea «Nota:» con «Fuente:» y hace que el texto largo sangre bajo su primera línea en vez de
volver al margen.

Un `&` de más manda el resto a una fila nueva y parte la línea a la mitad:

```latex
Nota: & Texto de la nota.\\      % correcto
& Nota: & Texto de la nota.\\    % rompe: tres celdas
```

Con varias fuentes, cada una en su renglón, repitiendo la celda vacía:

```latex
\tablefooter{Fuente: & CONAGUA. Disponibilidad en cuencas hidrológicas, 2023.\\
 & CONAGUA. Ordenamiento de aguas superficial, 2023.}
```

### Notas armadas desde el analizer

Cuando el bloque se genera en Python, la nota va en una constante del módulo y se pasa como argumento
opcional, no incrustada en la llamada. Así se lee de un vistazo y se cambia en un solo lugar.

```python
NOTA_PECUARIA = (
    "Se presenta el valor total de la producción de carne en canal, leche, "
    "huevo para plato, miel, cera y lana. No se contempla el valor de "
    "producción de ganado en pie."
)
```

El argumento es opcional para que las gráficas que no llevan nota conserven su pie de solo `Fuente:`.

## Cuándo la gráfica no existe

Cuando no hay datos suficientes, el analizer expone una bandera y el template envuelve el bloque:

```latex
<% if ge_tema_grafica_activa %>
...
<% endif %>
```

## Colores y estilo

El estilo de matplotlib es compartido y vive en `core/utils/charts.py`. Las paletas por tema están en
`pipelines/geografia/charts/palettes.py`.

En las gráficas apiladas el orden de los segmentos sigue el mapa explícito de colores del tema, y las
categorías residuales (`sin clasificación`, `otros`) van siempre al final. La leyenda sigue el orden
de aparición: de arriba hacia abajo, cada fila de izquierda a derecha.
