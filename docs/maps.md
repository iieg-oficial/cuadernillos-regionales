# Mapas

Referencia única para los mapas de los cuadernillos: de dónde salen, cómo se resuelven, cómo se
insertan en el template y qué gobierna su tamaño.

## Los mapas no se insertan con `\includegraphics`

A diferencia de las gráficas, el template **no** referencia el archivo del mapa. El analizer arma el
bloque LaTeX completo y lo pasa como variable de contexto:

```latex
\clearpage
\mapatitulo[\mapbleed]{Título del mapa de << ge_municipio >>, << ge_anio_mapa.tema >>}
<< ge_tema_mapa >>
```

La variable trae el `\includegraphics` con sus límites de tamaño ya resueltos. El template solo pone
el título y la variable.

## De dónde salen

Cada sección tiene su propio origen y su propia convención de nombres:

| Sección | Origen | Nombre del archivo |
|---|---|---|
| Geografía | `assets/maps/geografia/<tema>/` | `<tema>_<cvegeo>.png` |
| Demografía | `assets/maps/demografia/<subdir>/` | `<subdir>_<cvegeo>.png` |
| Historia | `assets/maps/historia/` | `ubicacion_<cvegeo>.png` |

`<cvegeo>` es la clave con el prefijo del estado: el municipio 39 es `14039`.

Los tres directorios están en `.gitignore`. Se descargan de Google Drive en la primera corrida, con
las URL de `.env/.env.geografia` y `.env/.env.demografia`, y no se vuelven a descargar si ya están.

Geografía comprueba que cada carpeta de tema tenga al menos 125 archivos antes de darla por completa.

### Temas de geografía

`TOPIC_FOLDERS` en `pipelines/geografia/helpers/maps.py` mapea la clave corta a su carpeta: `base` →
`mapa_base`, `geo` → `geologia`, `ed` → `edafologia`, y así con los 21 temas.

`FOLDER_ALIASES` da nombres alternativos para las carpetas que el área ha entregado con distinto
nombre: `pendientes` o `pendiente_clasificada`, `erosion_pot` o `erosion_potencial`. Si llega una
carpeta con un nombre nuevo, se agrega ahí en vez de renombrar los archivos.

### Cómo encuentra el archivo

`_find_map` no exige un nombre exacto: normaliza el nombre del archivo —sin acentos, en minúsculas— y
acepta que termine con la CVEGEO completa, con la clave de tres dígitos o con el nombre del municipio
normalizado. Eso absorbe las variaciones entre entregas.

Si no encuentra el mapa de un tema, usa `templates/assets/mapa_placeholder.png` y marca
`ge_<tema>_mapa_activo` en falso, para que el template pueda omitir la sección.

## Versión ligera

De cada mapa se guarda una versión comprimida en `output/maps/<seccion>/<cvegeo>/<clave>.jpg`:

| Parámetro | Valor |
|---|---|
| Alto máximo | 2000 px |
| Calidad JPEG | 82 |
| Transparencia | aplanada sobre blanco |

Se activa con `*_MAPS_QUALITY=draft` en el `.env` de cada sección; con `full` se usa el PNG original.

**El caché se invalida por fecha**: si el original es más reciente que el `.jpg`, se regenera solo.
Antes bastaba con que el `.jpg` existiera, y eso hacía que al recibir mapas nuevos se siguieran
sirviendo los viejos en silencio.

## Tamaño y posición

Dos longitudes de `templates/base.tex.j2` gobiernan la geometría:

| Longitud | Valor | Para qué |
|---|---|---|
| `\mapbleed` | 0.9 cm | Cuánto se extiende el mapa más allá del margen de texto, por lado |
| `\mapheadroom` | 1.6 cm | Espacio reservado para el título sobre el mapa |

El bloque que genera el analizer limita el mapa **por ancho y por alto**:

```latex
\hspace*{-\mapbleed}\makebox[<ancho>][c]{%
\adjustbox{max width=<ancho>,max height=\dimexpr\textheight-\mapheadroom\relax}{%
\includegraphics{...}}}
```

El límite de altura no es adorno: **la proporción de los mapas varía por municipio**. Los alargados
son más altos y, sin ese tope, no caben junto a su título y se brincan a la página siguiente. Con
Cuautitlán de García Barragán —relación alto/ancho de 1.2945 contra 1.2063 de Guadalajara— el mapa
resultaba más alto que la caja de página completa: no cabía ni sin título.

El `\makebox` centra el mapa sobre el ancho con sangrado, para que no se recorra cuando se encoge.

Los mapas de demografía no usan sangrado y van a `0.95\textwidth`, con holgura vertical de sobra.

## Título

`\mapatitulo[sangrado]{texto}` lleva su propio contador, así que la numeración es automática.

El título **se parte en dos líneas** cuando no cabe; no se encoge. Por eso `\mapheadroom` reserva
altura para dos renglones. Antes se encogía con `\resizebox`, lo que dejaba los títulos largos de
demografía visiblemente más chicos que los cortos de geografía.

El texto va en `colorTexto` y sin negritas.

## El contador es global

`\themapa` es un solo contador para todo el cuadernillo. El **Mapa 1** es el de localización de
Historia, que también usa `\mapatitulo`; los mapas de Geografía van del 2 al 22 y los de Demografía
del 23 al 25.

Historia arma su bloque en `pipelines/historia/analizer.py` y no aplica sangrado, así que su mapa
arranca en el margen de texto y no 0.9 cm a la izquierda como los de geografía.

## Pie de mapa

Se usa el mismo macro que las tablas, `\tablefooter`, sin `\vspace` extra, para que quede a ras de la
imagen. Ver [docs/tables.md](tables.md#pie-de-tabla) para el orden y el formato.

En geografía los pies de mapa están comentados en el template (`%\mapafuente{...}`) porque la fuente
ya aparece en el pie del cuadro correspondiente. Si se reactivan, deben migrarse a las variables
`ge_fuente.<tema>` del catálogo de fuentes, en vez de escribirse a mano.

## Años del título

Los años que aparecen en los títulos de mapa viven en `ANIO_MAPA`, dentro de
`pipelines/geografia/fuentes.py`, y se exponen como `ge_anio_mapa.<mapa>`. Cada entrada apunta a una
cita del catálogo, para que el año siga una sola fuente de verdad; solo el mapa base y el de
temperatura llevan el año como literal, porque el que indicó el área no corresponde a ninguna fuente
declarada.
