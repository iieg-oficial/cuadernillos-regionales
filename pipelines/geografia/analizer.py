from pathlib import Path

from core.constants import ND
from core.pipelines.stage import Stage
from core.utils.logger import Logger
from pipelines.geografia.charts.clima import (
    plot_precipitacion,
    plot_temperatura,
    plot_vientos,
)
from pipelines.geografia.charts.treemap import (
    plot_proportional_blocks,
    plot_stacked_pair,
)
from pipelines.geografia.fuentes import anios_desde_datos, build_fuentes_context
from pipelines.geografia.helpers.context import (
    append_unit,
    build_acuiferos_text,
    build_anp_text,
    build_clima_text,
    build_cuencas_disponibilidad_text,
    build_energia_text,
    build_espacios_publicos_text,
    build_linea_transmision_text,
    build_subestaciones_text,
    climate_context,
    municipal_value,
)
from pipelines.geografia.helpers.formatting import (
    first_value,
    fmt,
    fmt_int,
    fmt_no_cero,
    latex_escape,
    narrative_lower,
    pluralize_comparatives,
    sentence_case,
    strip_percent_symbol,
    to_number,
)
from pipelines.geografia.helpers.maps import resolve_maps
from pipelines.geografia.helpers.tables import (
    education_rows_for,
    health_rows_for,
    pct_sum,
    raw_sum,
    rows_for,
    sup_sum,
)

CHARTS_DIR = Path("output/charts")

SIN_CLASIFICACION = ["sin clasificacion", "sin clasificación"]

SIMPLE_CHART_TOPICS = [
    ("geologia", "categoria", "porcentaje", "orden_pct"),
    ("edafologia", "categoria", "porcentaje", "orden_pct"),
    ("uso_suelo", "categoria", "porcentaje", "orden_pct"),
    ("clima_koppen", "categoria", "porcentaje", "orden_pct"),
    ("sequia", "categoria", "porcentaje", "orden_clase"),
    ("pendiente_clasificada", "categoria", "porcentaje", "orden_clase"),
    ("itur_index_cat", "categoria", "porcentaje", "orden_pct"),
    ("ndvi", "categoria", "porcentaje", "orden_clase"),
    ("ndwi", "categoria", "porcentaje", "orden_clase"),
    ("erosion_potencial", "rango_texto", "porcentaje", "orden_clase"),
    ("erosion_efectiva", "rango_texto", "porcentaje", "orden_clase"),
]

# Claves de variables_texto que NO pasan al contexto: "nombre" choca entre temas y
# "anp_pct_anp" dejo de usarse al quitar la superficie del parrafo de ANP.
SKIP_TEXTO_KEYS = {
    "nombre",
    "anp_pct_anp",
}

INTEGER_KEYS = {
    "ge_edu_total_escuelas_muni",
    "ge_ie_dominante_valor",
}

TABLE_LABELS = {
    "ge_geo_unidades_geologicas": "Geología",
    "ge_ed_tipos_suelo": "Edafología",
    "ge_tp_pendientes": "Pendientes",
    "ge_cl_clasificaciones": "Clima",
    "ge_usv_clasificacion": "Uso de suelo y vegetación",
    "ge_ndvi_categorias": "NDVI",
    "ge_ndwi_categorias": "NDWI",
    "ge_anp_categorias": "Áreas naturales protegidas y humedales",
    "ge_ds_categorias": "Índice de sequía",
    "ge_er_categorias": "Erosión potencial",
    "ge_ee_categorias": "Erosión efectiva",
    "ge_itur_clasificaciones": "Índice Territorial Urbano-Rural",
    "ge_salud_unidades": "Unidades de salud",
    "ge_edu_centros": "Educación",
    "ge_ep_espacios": "Espacios públicos",
    "ge_ie_infraestructura": "Infraestructura energética",
}

NARRATIVE_LOWER_KEYS = [
    "ge_dg_pendiente_predom",
    "ge_dg_geo_predom",
    "ge_dg_edaf_predom",
    "ge_geo_dominante",
    "ge_geo_secundario",
    "ge_ed_dominante",
    "ge_ed_secundario",
    "ge_tp_dominante",
    "ge_tp_secundario",
    "ge_usv_dominante",
    "ge_usv_secundario",
    "ge_ndvi_dominante",
    "ge_ndvi_secundario",
    "ge_ndwi_dominante",
    "ge_ndwi_secundario",
    "ge_s_dominante",
    "ge_s_secundario",
    "ge_itur_dominante",
    "ge_itur_secundario",
    "ge_ie_dominante",
    "ge_er_dominante_rango",
    "ge_er_dominante_tipo",
    "ge_er_secundario_rango",
    "ge_ee_dominante_rango",
    "ge_ee_dominante_tipo",
    "ge_ee_secundario_rango",
]

PLURAL_SUBJECT_KEYS = [
    "ge_dg_pendiente_predom_texto",
    "ge_er_dominante_rango_texto",
    "ge_er_secundario_rango_texto",
    "ge_ee_dominante_rango_texto",
    "ge_ee_secundario_rango_texto",
]


def _chart_path(municipio_id, name):
    return CHARTS_DIR / municipio_id / f"ge_{name}.png"


def _erosion_range_label(value):
    text = str(value or "").strip()
    return {
        "0": "<= 0",
        "0.0": "<= 0",
        "Mayor a 0 y menor a 5": "0 - 5",
        "0 a 5": "0 - 5",
        "5 a 10": "5 - 10",
        "10 a 25": "10 - 25",
        "25 a 50": "25 - 50",
        "50 a 100": "50 - 100",
        "100 a 200": "100 - 200",
        "Más de 200": "> 200",
    }.get(text, text)


def _erosion_chart_label(row):
    rango = str(row.get("rango_texto") or "").strip()
    categoria = str(row.get("categoria") or "").strip()
    if categoria.lower() == "no susceptible" or rango in {"0", "0.0"}:
        return "<= 0 No susceptible"
    rango = _erosion_range_label(rango)
    return f"{rango} {categoria}".strip()


def _generate_simple_chart(detail_rows, topic_key, cat_col, val_col, sort_col, path):
    if not detail_rows:
        return False
    data = []
    for row in detail_rows:
        cat = (
            _erosion_chart_label(row)
            if topic_key.startswith("erosion_")
            else row.get(cat_col)
        )
        val = row.get(val_col)
        if cat and val is not None:
            try:
                data.append(
                    (str(cat), float(val), float(row.get(sort_col, 999) or 999))
                )
            except (ValueError, TypeError):
                pass
    if not data:
        return False
    data.sort(key=lambda x: x[2])
    data = [d for d in data if d[1] > 0]
    if not data:
        return False
    categories = [d[0] for d in data]
    values = [d[1] for d in data]
    try:
        plot_proportional_blocks(categories, values, topic_key, path)
        return True
    except Exception:
        return False


def _generate_stacked_chart(
    detail_rows_a, detail_rows_b, label_a, label_b, topic_key, path
):
    def _aggregate(rows):
        result = {}
        for row in rows:
            cat = sentence_case(str(row.get("categoria", "")))
            val = row.get("porcentaje")
            if cat and val is not None:
                try:
                    result[cat] = result.get(cat, 0) + float(val)
                except (ValueError, TypeError):
                    pass
        return result

    a = _aggregate(detail_rows_a)
    b = _aggregate(detail_rows_b)
    if not any(sum(d.values()) > 0 for d in [a, b]):
        return False
    try:
        plot_stacked_pair([(label_a, a), (label_b, b)], topic_key, path)
        return True
    except Exception:
        return False


def _pct_desde_superficie(rows, area_km2):
    area_ha = to_number(area_km2)
    if not area_ha:
        return rows
    area_ha *= 100
    ajustadas = []
    for row in rows:
        pct = to_number(row.get("porcentaje"))
        sup = to_number(row.get("superficie_ha"))
        if pct == 0 and sup:
            row = {**row, "porcentaje": sup / area_ha * 100}
        ajustadas.append(row)
    return ajustadas


def _fmt_field(val):
    if val is None:
        return ND
    if isinstance(val, float):
        return fmt(val)
    if isinstance(val, int) and not isinstance(val, bool):
        return fmt_int(val)
    return latex_escape(val)


class Analizer(Stage):
    def __init__(self, municipio_id: str):
        self.municipio_id = municipio_id

    def execute(self, input_data: dict) -> dict:
        municipio = input_data["municipio"]
        mid = str(self.municipio_id)
        dg = input_data["descripcion_general"]
        texto = input_data["texto"]
        detalle = input_data["detalle"]
        temp_long = input_data["temperatura_long"]
        temp_resumen = input_data["temperatura_resumen"]
        prec_long = input_data["precipitacion_long"]
        prec_resumen = input_data["precipitacion_resumen"]
        wind = input_data["wind"]

        ctx = {}

        ctx.update(build_fuentes_context(anios_desde_datos(detalle)))
        ctx["ge_municipio"] = latex_escape(municipio)
        ctx["ge_fecha_documento"] = "Abril 2026"

        for key, val in dg.items():
            if key == "dg_fid":
                continue
            ctx[f"ge_{key}"] = _fmt_field(val)

        ctx["ge_dg_municipio"] = ctx["ge_dg_nombre"]
        ctx["ge_dg_sup_mun_km2"] = ctx.get("ge_dg_area_km2", ND)
        ctx["ge_dg_nom_cabecera"] = ctx.get("ge_dg_nombre_cabecera", ND)
        ctx["ge_dg_cabecera_lat"] = ctx.get("ge_dg_lat", ND)
        ctx["ge_dg_cabecera_lon"] = ctx.get("ge_dg_lon", ND)
        ctx["ge_dg_cabecera_alt"] = ctx.get("ge_dg_elev1", ND)
        ctx["ge_dg_altitud_min"] = ctx.get("ge_dg_elevmin", ND)
        ctx["ge_dg_altitud_max"] = ctx.get("ge_dg_elevmax", ND)
        ctx["ge_dg_mun_colindantes"] = ctx.get("ge_dg_colindantes", ND)

        for topic, data in texto.items():
            for key, val in data.items():
                if key in SKIP_TEXTO_KEYS:
                    continue
                ctx_key = f"ge_{key}"
                ctx[ctx_key] = (
                    fmt_int(val) if ctx_key in INTEGER_KEYS else _fmt_field(val)
                )

        anp_texto = texto.get("anp_humedales_manglares", {})
        if anp_texto.get("anp_pct_humedales") is not None:
            ctx["ge_anp_pct_humedales"] = fmt_no_cero(anp_texto["anp_pct_humedales"])

        cl_texto = texto.get("clima_koppen", {})
        ctx["ge_dg_clima_predom"] = ctx.get(
            "ge_cl_tipo_predominante",
            latex_escape(cl_texto.get("cl_tipo_predominante")),
        )
        ctx["ge_dg_temp_media"] = ctx.get(
            "ge_tm_media_anual",
            fmt(temp_resumen.get("tm_media_anual")),
        )
        ctx["ge_dg_prec_acum"] = ctx.get(
            "ge_p_acumulada_anual",
            fmt(prec_resumen.get("p_acumulada_anual")),
        )

        geo_texto = texto.get("geologia", {})
        ctx["ge_dg_geo_predom"] = ctx.get(
            "ge_geo_dominante",
            latex_escape(geo_texto.get("geo_dominante")),
        )
        ed_texto = texto.get("edafologia", {})
        ctx["ge_dg_edaf_predom"] = ctx.get(
            "ge_ed_dominante",
            latex_escape(ed_texto.get("ed_dominante")),
        )
        tp_texto = texto.get("pendiente_clasificada", {})
        ctx["ge_dg_pendiente_predom"] = ctx.get(
            "ge_tp_dominante",
            latex_escape(tp_texto.get("tp_dominante")),
        )

        vientos = texto.get("vientos_dominantes", {})
        wind_dir = first_value(vientos, "dg_viento_predom")
        ctx["ge_dg_viento_predom"] = latex_escape(wind_dir) if wind_dir else ND
        wind_fr = strip_percent_symbol(first_value(vientos, "dg_viento_predom_fr"))
        ctx["ge_dg_viento_predom_fr"] = fmt(to_number(wind_fr)) if wind_fr else ND

        ctx.update({f"ge_{k}": v for k, v in climate_context(temp_long, "tm").items()})
        ctx.update({f"ge_{k}": v for k, v in climate_context(prec_long, "pp").items()})

        for key in ["tm_media_anual", "t_media_anual"]:
            if temp_resumen.get(key) is not None:
                ctx[f"ge_{key}"] = fmt(temp_resumen[key])

        for key in temp_resumen:
            if key != "municipio" and f"ge_{key}" not in ctx:
                ctx[f"ge_{key}"] = _fmt_field(temp_resumen[key])

        for key in ["ge_t_valores_menor_temp", "ge_t_valores_mayor_temp"]:
            ctx[key] = append_unit(ctx.get(key), "°C")

        for key in prec_resumen:
            if key != "municipio" and f"ge_{key}" not in ctx:
                ctx[f"ge_{key}"] = _fmt_field(prec_resumen[key])

        ctx["ge_geo_unidades_geologicas"] = rows_for(
            detalle.get("geologia", []),
            {
                "roca": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
            },
        )
        ctx["ge_ed_tipos_suelo"] = rows_for(
            detalle.get("edafologia", []),
            {
                "tipo_suelo": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
            },
        )
        ctx["ge_tp_pendientes"] = rows_for(
            detalle.get("pendiente_clasificada", []),
            {
                "categoria": "categoria",
                "superficie_ha": "superficie_ha_aj",
                "porcentaje": "porcentaje",
            },
            order_col="orden_clase",
        )
        ctx["ge_cl_clasificaciones"] = rows_for(
            detalle.get("clima_koppen", []),
            {
                "clasificacion_climatica": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
            },
        )
        ctx["ge_usv_clasificacion"] = rows_for(
            detalle.get("uso_suelo", []),
            {
                "grupo": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
            },
        )
        ctx["ge_ndvi_categorias"] = rows_for(
            detalle.get("ndvi", []),
            {
                "categoria": "categoria",
                "superficie_ha_aj": "superficie_ha_aj",
                "porcentaje": "porcentaje",
            },
            order_col="orden_clase",
        )
        ctx["ge_ndwi_categorias"] = rows_for(
            detalle.get("ndwi", []),
            {
                "categoria": "categoria",
                "superficie_ha_aj": "superficie_ha_aj",
                "porcentaje": "porcentaje",
            },
            order_col="orden_clase",
        )
        ctx["ge_anp_categorias"] = rows_for(
            _pct_desde_superficie(
                detalle.get("anp_humedales_manglares", []), dg.get("dg_area_km2")
            ),
            {
                "categoria": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
                "descripcion": "cadena_texto",
            },
            transforms={"porcentaje": fmt_no_cero},
        )
        ctx["ge_ds_categorias"] = rows_for(
            detalle.get("sequia", []),
            {
                "categoria": "categoria",
                "superficie_ha": "superficie_ha_aj",
                "porcentaje": "porcentaje",
            },
            order_col="orden_clase",
        )
        ctx["ge_er_categorias"] = rows_for(
            detalle.get("erosion_potencial", []),
            {
                "categoria": "rango_texto",
                "superficie_ha": "superficie_ha_aj",
                "porcentaje": "porcentaje",
            },
            order_col="orden_clase",
        )
        ctx["ge_ee_categorias"] = rows_for(
            detalle.get("erosion_efectiva", []),
            {
                "categoria": "rango_texto",
                "superficie_ha": "superficie_ha_aj",
                "porcentaje": "porcentaje",
            },
            order_col="orden_clase",
        )
        ctx["ge_itur_clasificaciones"] = rows_for(
            detalle.get("itur_index_cat", []),
            {
                "categoria": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
            },
        )
        ctx["ge_salud_unidades"] = health_rows_for(
            detalle.get("salud_nivel_atencion", [])
        )
        ctx["ge_edu_centros"] = education_rows_for(detalle.get("educacion_nivel", []))
        ctx["ge_ep_espacios"] = rows_for(
            detalle.get("espacios_publicos", []),
            {
                "tipo": "categoria",
                "superficie_ha": "conteo",
                "porcentaje": "porcentaje",
            },
        )
        ctx["ge_ie_infraestructura"] = rows_for(
            detalle.get("denue_energia", []),
            {
                "tipo_infraestructura": "categoria",
                "valor": "conteo",
                "porcentaje": "porcentaje",
            },
        )

        for key, label in TABLE_LABELS.items():
            if not ctx.get(key):
                Logger.warning(
                    f"Geografía: municipio {municipio} sin datos de {label}, "
                    "tabla omitida"
                )

        cu_clasificac = detalle.get("cuencas_clasificac", [])
        cu_categ = detalle.get("cuencas_categ", [])
        ac_sit = detalle.get("acuiferos_situacion", [])
        ac_cond = detalle.get("acuiferos_condicion", [])
        linea_t = detalle.get("linea_transm_l", [])

        ctx["ge_cu_pct_con_disponibilidad"] = pct_sum(
            cu_clasificac, ["con disponibilidad"]
        )
        ctx["ge_cu_pct_sin_disponibilidad"] = pct_sum(
            cu_clasificac, ["sin disponibilidad"]
        )
        ctx["ge_cu_disponibilidad"] = rows_for(
            cu_clasificac,
            {
                "categoria": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
            },
            transforms={"categoria": sentence_case},
        )
        ctx["ge_cu_ordenamiento"] = rows_for(
            cu_categ,
            {
                "categoria": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
            },
            transforms={"categoria": sentence_case},
        )
        ctx["ge_cu_disponibilidad_texto"] = build_cuencas_disponibilidad_text(
            ctx["ge_cu_pct_con_disponibilidad"],
            ctx["ge_cu_pct_sin_disponibilidad"],
        )
        ctx["ge_ac_sup_con_disponibilidad"] = sup_sum(ac_sit, ["con disponibilidad"])
        ctx["ge_ac_pct_con_disponibilidad"] = pct_sum(ac_sit, ["con disponibilidad"])
        ctx["ge_ac_sup_sin_disponibilidad"] = sup_sum(ac_sit, ["sin disponibilidad"])
        ctx["ge_ac_pct_sin_disponibilidad"] = pct_sum(ac_sit, ["sin disponibilidad"])
        ctx["ge_ac_sup_sobreexplotado"] = sup_sum(ac_cond, ["sobreexplotado"])
        ctx["ge_ac_pct_sobreexplotado"] = pct_sum(ac_cond, ["sobreexplotado"])
        ctx["ge_ac_sup_no_sobreexplotado"] = sup_sum(
            ac_cond, ["no explotado", "no sobreexplotado"]
        )
        ctx["ge_ac_pct_no_sobreexplotado"] = pct_sum(
            ac_cond, ["no explotado", "no sobreexplotado"]
        )
        ctx["ge_ac_sit_sin_clasificacion_activa"] = (
            raw_sum(ac_sit, SIN_CLASIFICACION) > 0
        )
        ctx["ge_ac_sup_sit_sin_clasificacion"] = sup_sum(ac_sit, SIN_CLASIFICACION)
        ctx["ge_ac_pct_sit_sin_clasificacion"] = pct_sum(ac_sit, SIN_CLASIFICACION)
        ctx["ge_ac_cond_sin_clasificacion_activa"] = (
            raw_sum(ac_cond, SIN_CLASIFICACION) > 0
        )
        ctx["ge_ac_sup_cond_sin_clasificacion"] = sup_sum(ac_cond, SIN_CLASIFICACION)
        ctx["ge_ac_pct_cond_sin_clasificacion"] = pct_sum(ac_cond, SIN_CLASIFICACION)
        ctx["ge_ac_texto"] = build_acuiferos_text(
            ctx.get("ge_ac_nombres_acuiferos"),
            ctx["ge_ac_pct_con_disponibilidad"],
            ctx["ge_ac_pct_sin_disponibilidad"],
            ctx["ge_ac_pct_sit_sin_clasificacion"],
        )

        salud_total = to_number(
            texto.get("salud_nivel_atencion", {}).get("salud_total_puntos_muni")
        )
        ctx["ge_salud_total_puntos_muni"] = (
            fmt_int(salud_total) if salud_total is not None else ND
        )
        ctx["ge_salud_total_unidades"] = ctx["ge_salud_total_puntos_muni"]
        subestaciones = detalle.get("subestacion", [])
        subestaciones_total = municipal_value(subestaciones, "conteo_total_municipio")
        ctx["ge_ene_conteo_total_municipio"] = (
            fmt_int(subestaciones_total) if subestaciones_total is not None else ND
        )
        ctx["ge_ene_linea_transm_l_km"] = fmt(
            municipal_value(linea_t, "longitud_km_total_municipio")
        )

        anp_ctx = {}
        for k, v in ctx.items():
            if k.startswith("ge_anp_") or k.startswith("ge_dg_"):
                anp_ctx[k.removeprefix("ge_")] = v
        anp_ctx["municipio"] = municipio
        ctx["ge_anp_texto_automatico"] = build_anp_text(anp_ctx)
        ctx["ge_ep_resumen_texto"] = build_espacios_publicos_text(
            municipio,
            ctx.get("ge_ep_total_puntos_muni"),
            detalle.get("espacios_publicos", []),
        )
        ctx["ge_ene_subestaciones_texto"] = build_subestaciones_text(
            subestaciones_total
        )
        ctx["ge_ene_linea_transm_l_texto"] = build_linea_transmision_text(
            municipal_value(linea_t, "longitud_km_total_municipio")
        )
        for key in NARRATIVE_LOWER_KEYS:
            ctx[f"{key}_texto"] = narrative_lower(ctx.get(key, "ND"))
        for key in PLURAL_SUBJECT_KEYS:
            ctx[key] = pluralize_comparatives(ctx.get(key))

        ctx["ge_ie_texto"] = build_energia_text(
            ctx.get("ge_ie_dominante_texto"),
            ctx.get("ge_ie_dominante_valor", ND),
            ctx.get("ge_ie_dominante_pct", ND),
            ctx.get("ge_ie_tipos_secundarios"),
        )
        ctx["ge_cl_texto"] = build_clima_text(
            municipio,
            ctx.get("ge_cl_tipo_predominante"),
            ctx.get("ge_cl_pct_predominante", ND),
            ctx.get("ge_cl_secundario"),
            ctx.get("ge_cl_secundario_pct", ND),
            ctx.get("ge_cl_otros_nombres"),
            ctx.get("ge_cl_otros_pct", ND),
        )

        Logger.info("Geografía: generando gráficas")
        for topic, cat_col, val_col, sort_col in SIMPLE_CHART_TOPICS:
            chart_name = {
                "geologia": "geo",
                "edafologia": "ed",
                "pendiente_clasificada": "tp",
                "clima_koppen": "cl",
                "uso_suelo": "usv",
                "itur_index_cat": "itur",
                "erosion_potencial": "er",
                "erosion_efectiva": "ee",
            }.get(topic, topic)
            path = _chart_path(mid, chart_name)
            ok = _generate_simple_chart(
                detalle.get(topic, []), topic, cat_col, val_col, sort_col, path
            )
            ctx[f"ge_{chart_name}_grafica"] = str(path) if ok else ""
            ctx[f"ge_{chart_name}_grafica_activa"] = ok

        cu_path = _chart_path(mid, "cu")
        cu_ok = _generate_stacked_chart(
            cu_categ,
            cu_clasificac,
            "Ordenamiento",
            "Disponibilidad",
            "cuencas",
            cu_path,
        )
        ctx["ge_cu_grafica"] = str(cu_path) if cu_ok else ""
        ctx["ge_cu_grafica_activa"] = cu_ok

        ac_path = _chart_path(mid, "ac")
        ac_ok = _generate_stacked_chart(
            ac_cond, ac_sit, "Condición", "Situación", "acuiferos", ac_path
        )
        ctx["ge_ac_grafica"] = str(ac_path) if ac_ok else ""
        ctx["ge_ac_grafica_activa"] = ac_ok

        tm_path = _chart_path(mid, "tm")
        if temp_long:
            try:
                plot_temperatura(temp_long, tm_path)
                ctx["ge_tm_grafica"] = str(tm_path)
                ctx["ge_tm_grafica_activa"] = True
            except Exception:
                ctx["ge_tm_grafica"] = ""
                ctx["ge_tm_grafica_activa"] = False
        else:
            ctx["ge_tm_grafica"] = ""
            ctx["ge_tm_grafica_activa"] = False

        pp_path = _chart_path(mid, "pp")
        if prec_long:
            try:
                plot_precipitacion(prec_long, pp_path)
                ctx["ge_pp_grafica"] = str(pp_path)
                ctx["ge_pp_grafica_activa"] = True
            except Exception:
                ctx["ge_pp_grafica"] = ""
                ctx["ge_pp_grafica_activa"] = False
        else:
            ctx["ge_pp_grafica"] = ""
            ctx["ge_pp_grafica_activa"] = False

        viento_path = _chart_path(mid, "viento")
        if wind:
            try:
                plot_vientos(wind, viento_path)
                ctx["ge_dg_viento_grafica"] = str(viento_path)
                ctx["ge_dg_viento_grafica_activa"] = True
            except Exception:
                ctx["ge_dg_viento_grafica"] = ""
                ctx["ge_dg_viento_grafica_activa"] = False
        else:
            ctx["ge_dg_viento_grafica"] = ""
            ctx["ge_dg_viento_grafica_activa"] = False

        Logger.info("Geografía: resolviendo mapas")
        ctx.update(resolve_maps(input_data["cve_geo"], municipio))
        Logger.info("Geografía: análisis completo")

        return ctx
