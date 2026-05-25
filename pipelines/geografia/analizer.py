from pathlib import Path

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
from pipelines.geografia.helpers.context import (
    build_anp_text,
    build_linea_transmision_text,
    climate_context,
    municipal_value,
)
from pipelines.geografia.helpers.formatting import (
    first_value,
    fmt,
    strip_percent_symbol,
)
from pipelines.geografia.helpers.maps import resolve_maps
from pipelines.geografia.helpers.tables import (
    education_rows_for,
    health_rows_for,
    pct_sum,
    rows_for,
    sup_sum,
)

CHARTS_DIR = Path("output/charts")

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


def _chart_path(municipio_id, name):
    return CHARTS_DIR / municipio_id / f"ge_{name}.png"


def _generate_simple_chart(detail_rows, topic_key, cat_col, val_col, sort_col, path):
    if not detail_rows:
        return False
    data = []
    for row in detail_rows:
        cat = row.get(cat_col)
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
            cat = str(row.get("categoria", ""))
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


class Analizer(Stage):
    def __init__(self, municipio_id):
        self.municipio_id = municipio_id

    def execute(self, input_data):
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

        ctx["ge_municipio"] = fmt(municipio, field_name="municipio")
        ctx["ge_fecha_documento"] = "Abril 2026"

        for key, val in dg.items():
            if key == "dg_fid":
                continue
            ctx[f"ge_{key}"] = fmt(val, field_name=key)

        ctx["ge_dg_municipio"] = ctx["ge_dg_nombre"]
        ctx["ge_dg_sup_mun_km2"] = ctx.get("ge_dg_area_km2", "ND")
        ctx["ge_dg_nom_cabecera"] = ctx.get("ge_dg_nombre_cabecera", "ND")
        ctx["ge_dg_cabecera_lat"] = ctx.get("ge_dg_lat", "ND")
        ctx["ge_dg_cabecera_lon"] = ctx.get("ge_dg_lon", "ND")
        ctx["ge_dg_cabecera_alt"] = ctx.get("ge_dg_elev1", "ND")
        ctx["ge_dg_altitud_min"] = ctx.get("ge_dg_elevmin", "ND")
        ctx["ge_dg_altitud_max"] = ctx.get("ge_dg_elevmax", "ND")
        ctx["ge_dg_mun_colindantes"] = ctx.get("ge_dg_colindantes", "ND")

        for topic, data in texto.items():
            for key, val in data.items():
                if key == "nombre":
                    continue
                ctx[f"ge_{key}"] = fmt(val, field_name=key)

        cl_texto = texto.get("clima_koppen", {})
        ctx["ge_dg_clima_predom"] = ctx.get(
            "ge_cl_tipo_predominante",
            fmt(
                cl_texto.get("cl_tipo_predominante"), field_name="cl_tipo_predominante"
            ),
        )
        ctx["ge_dg_temp_media"] = ctx.get(
            "ge_tm_media_anual",
            fmt(temp_resumen.get("tm_media_anual"), field_name="tm_media_anual"),
        )
        ctx["ge_dg_prec_acum"] = ctx.get(
            "ge_p_acumulada_anual",
            fmt(prec_resumen.get("p_acumulada_anual"), field_name="p_acumulada_anual"),
        )

        geo_texto = texto.get("geologia", {})
        ctx["ge_dg_geo_predom"] = ctx.get(
            "ge_geo_dominante",
            fmt(geo_texto.get("geo_dominante"), field_name="geo_dominante"),
        )
        ed_texto = texto.get("edafologia", {})
        ctx["ge_dg_edaf_predom"] = ctx.get(
            "ge_ed_dominante",
            fmt(ed_texto.get("ed_dominante"), field_name="ed_dominante"),
        )
        tp_texto = texto.get("pendiente_clasificada", {})
        ctx["ge_dg_pendiente_predom"] = ctx.get(
            "ge_tp_dominante",
            fmt(tp_texto.get("tp_dominante"), field_name="tp_dominante"),
        )

        vientos = texto.get("vientos_dominantes", {})
        ctx["ge_dg_viento_predom"] = fmt(
            first_value(vientos, "dg_viento_predom", default="ND"),
            field_name="dg_viento_predom",
        )
        ctx["ge_dg_viento_predom_fr"] = fmt(
            strip_percent_symbol(
                first_value(vientos, "dg_viento_predom_fr", default="ND")
            ),
            field_name="dg_viento_predom_fr",
        )

        ctx.update({f"ge_{k}": v for k, v in climate_context(temp_long, "tm").items()})
        ctx.update({f"ge_{k}": v for k, v in climate_context(prec_long, "pp").items()})

        for key in ["tm_media_anual", "t_media_anual"]:
            if temp_resumen.get(key) is not None:
                ctx[f"ge_{key}"] = fmt(temp_resumen[key], field_name=key)

        for key in temp_resumen:
            if key != "municipio" and f"ge_{key}" not in ctx:
                ctx[f"ge_{key}"] = fmt(temp_resumen[key], field_name=key)

        for key in prec_resumen:
            if key != "municipio" and f"ge_{key}" not in ctx:
                ctx[f"ge_{key}"] = fmt(prec_resumen[key], field_name=key)

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
            detalle.get("anp_humedales_manglares", []),
            {
                "categoria": "categoria",
                "superficie_ha": "superficie_ha",
                "porcentaje": "porcentaje",
                "descripcion": "cadena_texto",
            },
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

        cu_clasificac = detalle.get("cuencas_clasificac", [])
        cu_categ = detalle.get("cuencas_categ", [])
        ac_sit = detalle.get("acuiferos_situacion", [])
        ac_cond = detalle.get("acuiferos_condicion", [])
        linea_t = detalle.get("linea_transm_l", [])

        ctx["ge_cu_sup_con_disponibilidad"] = sup_sum(
            cu_clasificac, ["con disponibilidad"]
        )
        ctx["ge_cu_pct_con_disponibilidad"] = pct_sum(
            cu_clasificac, ["con disponibilidad"]
        )
        ctx["ge_cu_sup_sin_disponibilidad"] = sup_sum(
            cu_clasificac, ["sin disponibilidad"]
        )
        ctx["ge_cu_pct_sin_disponibilidad"] = pct_sum(
            cu_clasificac, ["sin disponibilidad"]
        )
        ctx["ge_cu_sup_reserva"] = sup_sum(cu_categ, ["reserva"])
        ctx["ge_cu_pct_reserva"] = pct_sum(cu_categ, ["reserva"])
        ctx["ge_cu_sup_veda"] = sup_sum(cu_categ, ["veda"])
        ctx["ge_cu_pct_veda"] = pct_sum(cu_categ, ["veda"])
        ctx["ge_cu_sup_veda_reglamento"] = sup_sum(cu_categ, ["veda y reglamento"])
        ctx["ge_cu_pct_veda_reglamento"] = pct_sum(cu_categ, ["veda y reglamento"])
        ctx["ge_cu_sup_veda_reserva_reglamento"] = sup_sum(
            cu_categ, ["veda, reserva y reglamento"]
        )
        ctx["ge_cu_pct_veda_reserva_reglamento"] = pct_sum(
            cu_categ, ["veda, reserva y reglamento"]
        )
        ctx["ge_cu_sup_sin_ordenamiento_superficial"] = sup_sum(
            cu_categ, ["sin ordenamiento"]
        )
        ctx["ge_cu_pct_sin_ordenamiento_superficial"] = pct_sum(
            cu_categ, ["sin ordenamiento"]
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

        ctx["ge_salud_total_unidades"] = ctx.get("ge_salud_total_puntos_muni", "ND")
        ctx["ge_ene_conteo_total_municipio"] = ctx.get(
            "ge_ie_conteo_total_municipio", "ND"
        )
        ctx["ge_ene_linea_transm_l_km"] = fmt(
            municipal_value(linea_t, "longitud_km_total_municipio"),
            field_name="longitud_km_total_municipio",
        )

        anp_ctx = {}
        for k, v in ctx.items():
            if k.startswith("ge_anp_") or k.startswith("ge_dg_"):
                anp_ctx[k.removeprefix("ge_")] = v
        anp_ctx["municipio"] = municipio
        ctx["ge_anp_texto_automatico"] = build_anp_text(anp_ctx)
        ctx["ge_ene_linea_transm_l_texto"] = build_linea_transmision_text(
            municipal_value(linea_t, "longitud_km_total_municipio")
        )

        Logger.info("Geografía: generando gráficas...")
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

        Logger.info("Geografía: resolviendo mapas...")
        ctx.update(resolve_maps(input_data["cve_geo"], municipio))
        Logger.info("Geografía: análisis completo")

        return ctx
