# Reglas de formato de datos

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

El separador de miles es un **espacio** (`\,` en LaTeX), no una coma ni un punto.

- Correcto: `1 500`, `12 340.50`, `1 234 567`
- Incorrecto: `1,500`, `1.500`, `1500`

En LaTeX, usar `\,` para el espacio fino de miles:

```latex
1\,500
12\,340.50
```

Esta regla aplica solo a **valores numéricos**. No aplica a:
- Claves o IDs
- Años
- Rankings o posiciones

## Aplicación en el analizer

El formateo se aplica en Python antes de pasar los datos al contexto Jinja2, no en el template. Usar una función helper centralizada:

```python
def fmt(value):
    if value is None:
        return r"\ND"
    return f"{value:,.2f}".replace(",", "\u2009")
```

El template solo inserta la variable ya formateada: `<< variable >>`.
