# Reglas de formato de datos

Basado en la Norma Oficial Mexicana NOM-008-SE-2021 (Sistema General de Unidades de Medida).

## Decimales

Los valores numéricos se muestran con exactamente 2 decimales.

- Correcto: `12.50`, `1 234.67`, `0.03`
- Incorrecto: `12.5`, `12`, `12.500`

Esta regla aplica solo a **valores** (porcentajes, índices, cantidades). No aplica a:
- Claves o IDs (e.g. `0101`, `14039`)
- Años (e.g. `2020`)
- Rankings o posiciones (e.g. `lugar 3`)
- Grados cualitativos (e.g. `Alto`, `Muy bajo`)

## Separador de miles

El separador de miles es un **espacio de no separación** entre grupos de tres dígitos, no una coma ni un punto.

- Correcto: `1 500`, `12 340.50`, `1 234 567`
- Incorrecto: `1,500`, `1.500`, `1500`

En LaTeX, usar `\,` para el espacio fino de no separación:

```latex
1\,500
12\,340.50
1\,234\,567
```

Esta regla aplica solo a **valores numéricos**. No aplica a:
- Claves o IDs
- Años
- Rankings o posiciones

## Cifra con unidad de medida

Separar la cifra del símbolo de unidad con un **espacio de no separación**. Los símbolos NO llevan punto al final y son invariables en singular y plural.

- Correcto: `234 km`, `45 min`, `1 000 000 ha`, `10:00 h`
- Incorrecto: `234km`, `45 min.`, `1000000 ha`

En LaTeX:

```latex
234\,km
45\,min
1\,000\,000\,ha
```

**Excepción:** Los símbolos `°`, `'` y `"` (grado, minuto y segundo de arco) van pegados a la cifra, sin espacio:

```latex
5°
36'
18"
```

## Porcentaje

El símbolo `%` se separa de la cifra con un **espacio de no separación**.

- Correcto: `35 %`, `0.05 %`, `1.18 %`
- Incorrecto: `35%`, `0.05%`

En LaTeX:

```latex
35\,\%
0.05\,\%
1.18\,\%
```

## Aplicación en el analizer

El formateo se aplica en Python antes de pasar los datos al contexto Jinja2, no en el template. Usar funciones helper centralizadas:

```python
THIN_SPACE = " "

def fmt(value):
    if value is None:
        return r"\ND"
    return f"{value:,.2f}".replace(",", THIN_SPACE)

def fmt_pct(value):
    if value is None:
        return r"\ND"
    formatted = f"{value:,.2f}".replace(",", THIN_SPACE)
    return rf"{formatted}\,\%"

def fmt_int(value):
    if value is None:
        return r"\ND"
    return f"{int(value):,}".replace(",", THIN_SPACE)
```

El template solo inserta la variable ya formateada: `<< variable >>`.
