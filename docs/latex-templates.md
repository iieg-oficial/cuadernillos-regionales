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

Todas las tablas del proyecto usan `longtable` — no `tabular`. Si tu `.tex` de Overleaf usa `\begin{tabular}`, cámbialo a `\begin{longtable}`.

Las columnas se definen con proporciones de `\linewidth` que sumen 1.00, restando siempre `2\tabcolsep`:

En Overleaf:

```latex
\begin{tabular}{|c|l|c|c|}
```

En el template:

```latex
\begin{longtable}{|>{\centering\arraybackslash}p{\dimexpr0.15\linewidth - 2\tabcolsep\relax}
                  |>{\raggedright\arraybackslash}p{\dimexpr0.45\linewidth - 2\tabcolsep\relax}
                  |>{\centering\arraybackslash}p{\dimexpr0.20\linewidth - 2\tabcolsep\relax}
                  |>{\centering\arraybackslash}p{\dimexpr0.20\linewidth - 2\tabcolsep\relax}|}
```

La alineación dentro de cada columna la defines según el contenido:

| Alineación | Comando | Cuándo usarla |
|---|---|---|
| Centrado | `\centering\arraybackslash` | Números, claves, porcentajes |
| Izquierda | `\raggedright\arraybackslash` | Texto largo (nombres, etiquetas) |
| Derecha | `\raggedleft\arraybackslash` | Montos, valores con decimales alineados |

Las proporciones (0.15 + 0.45 + 0.20 + 0.20 = 1.00) las defines tú según el contenido.

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
