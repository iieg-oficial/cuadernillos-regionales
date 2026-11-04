import json
import math
from decimal import Decimal
from pathlib import Path

from core.pipelines.stage import Stage
from pipelines.geografia.charts.clima import (
    MONTH_ORDER,
    plot_precipitacion,
    plot_temperatura,
    plot_vientos,
)
from pipelines.geografia.charts.treemap import (
    plot_proportional_blocks,
    plot_stacked_pair,
)
from pipelines.geografia.fuentes import build_fuentes_context
from pipelines.geografia.helpers.formatting import (
    fmt,
    fmt_int,
    fmt_no_cero,
    fmt_pct,
    latex_escape,
)
from pipelines.geografia.helpers.maps import resolve_maps

CHARTS_DIR = Path("output/charts/regiones")
WIND_DATA = Path("assets/maps/geografia/regiones/viento_era5_2025.json")
RUMBOS = "norte noreste este sureste sur suroeste oeste noroeste".split()

DISTRIBUCIONES = (
    ("geo", "ge_geo_unidades_geologicas", "roca", "geologia"),
    ("ed", "ge_ed_tipos_suelo", "tipo_suelo", "edafologia"),
    ("tp", "ge_tp_pendientes", "categoria", "pendiente_clasificada"),
    ("cl", "ge_cl_clasificaciones", "clasificacion_climatica", "clima_koppen"),
    ("usv", "ge_usv_clasificacion", "grupo", "uso_suelo"),
    ("ndvi", "ge_ndvi_categorias", "categoria", "ndvi"),
    ("ndwi", "ge_ndwi_categorias", "categoria", "ndwi"),
    ("sequia", "ge_ds_categorias", "categoria", "sequia"),
    ("er", "ge_er_categorias", "categoria", "erosion_potencial"),
    ("ee", "ge_ee_categorias", "categoria", "erosion_efectiva"),
    ("itur", "ge_itur_clasificaciones", "categoria", "itur_index_cat"),
)


def _format(key, value):
    if isinstance(value, int):
        return fmt_int(value)
    if isinstance(value, Decimal | float):
        if key.endswith(("_lat", "_lon")):
            return fmt(value, 6)
        if "indice" in key:
            return fmt_no_cero(value, 4, 5)
        return fmt_no_cero(value)
    return latex_escape(value)


def _distribution(rows, category):
    return {
        row[category]: float(row["porcentaje"])
        for row in rows
        if row["porcentaje"] is not None and row["porcentaje"] > 0
    }


def _monthly(scalars, topic):
    return [
        {
            "periodo": month,
            "min": scalars[f"ge_{topic}_min_{month.lower()}"],
            "mean": scalars[f"ge_{topic}_med_{month.lower()}"],
            "max": scalars[f"ge_{topic}_max_{month.lower()}"],
        }
        for month in MONTH_ORDER
    ]


def _wind(clave, scalars):
    if not WIND_DATA.is_file():
        return {}
    frequencies = json.loads(WIND_DATA.read_text(encoding="utf-8")).get(clave)
    if frequencies is None:
        return {}
    if (
        set(frequencies) != set(RUMBOS)
        or any(not 0 <= p <= 100 for p in frequencies.values())
        or not math.isclose(sum(frequencies.values()), 100, abs_tol=1e-6)
    ):
        raise ValueError(f"Frecuencias ERA5 inválidas para la región {clave}")
    winner = max(RUMBOS, key=frequencies.__getitem__)
    expected = scalars["ge_dg_viento_predom_fr"]
    if (
        winner != scalars["ge_dg_viento_predom"]
        or expected is None
        or not math.isclose(frequencies[winner], float(expected), abs_tol=1e-6)
    ):
        raise ValueError(f"El insumo ERA5 no coincide con el indicador de {clave}")
    return {
        f"grado_{angle}": frequencies[rumbo] / 100
        for angle, rumbo in zip(range(0, 360, 45), RUMBOS, strict=True)
    }


class Analizer(Stage):
    def __init__(self, clave):
        self.clave = clave

    def execute(self, input_data):
        scalars, details = input_data
        ctx = {key: _format(key, value) for key, value in scalars.items()}
        ctx.update(
            {
                table: [
                    {key: _format(key, value) for key, value in row.items()}
                    for row in rows
                ]
                for table, rows in details.items()
            }
        )
        ctx.update(build_fuentes_context())
        ctx.update(resolve_maps(self.clave))
        ctx["ge_cl_fuente_cartografica"] = "la cartografía Köppen–García"
        ctx["ge_ene_anio"] = ctx["ge_anio"]["energia"]
        viento = scalars["ge_dg_viento_predom"]
        ctx["ge_dg_viento_frecuencia"] = fmt_pct(scalars["ge_dg_viento_predom_fr"])
        ctx["ge_dg_viento_origen"] = (
            f"del {latex_escape(viento)}" if viento in RUMBOS else latex_escape(None)
        )

        def chart(topic, plot, *args, active):
            path = CHARTS_DIR / self.clave / f"ge_{topic}.png"
            if active:
                plot(*args, path)
            ctx[f"ge_{topic}_grafica_activa"] = bool(active)
            ctx[f"ge_{topic}_grafica"] = path.as_posix() if active else ""

        for topic, table, category, palette in DISTRIBUCIONES:
            values = _distribution(details[table], category)
            chart(
                topic,
                plot_proportional_blocks,
                list(values),
                list(values.values()),
                palette,
                active=values,
            )
        cuencas = [
            ("Ordenamiento", _distribution(details["ge_cu_ordenamiento"], "categoria")),
            (
                "Disponibilidad",
                _distribution(details["ge_cu_disponibilidad"], "categoria"),
            ),
        ]
        acuiferos = [
            (
                "Condición",
                {
                    "No sobreexplotado": scalars["ge_ac_pct_no_sobreexplotado"],
                    "Sobreexplotado": scalars["ge_ac_pct_sobreexplotado"],
                },
            ),
            (
                "Disponibilidad",
                {
                    "Con disponibilidad": scalars["ge_ac_pct_con_disponibilidad"],
                    "Sin disponibilidad": scalars["ge_ac_pct_sin_disponibilidad"],
                },
            ),
        ]
        acuiferos = [
            (
                label,
                {
                    name: float(value)
                    for name, value in row.items()
                    if value is not None
                },
            )
            for label, row in acuiferos
        ]
        chart(
            "cu",
            plot_stacked_pair,
            cuencas,
            "cuencas",
            active=any(row for _, row in cuencas),
        )
        chart(
            "ac",
            plot_stacked_pair,
            acuiferos,
            "acuiferos",
            active=any(row for _, row in acuiferos),
        )
        for topic, plot in (("tm", plot_temperatura), ("pp", plot_precipitacion)):
            monthly = _monthly(scalars, topic)
            chart(
                topic,
                plot,
                monthly,
                active=all(
                    row[key] is not None
                    for row in monthly
                    for key in ("min", "mean", "max")
                ),
            )
        wind = _wind(self.clave, scalars)
        chart("dg_viento", plot_vientos, wind, active=wind)
        return ctx
