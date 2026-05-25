from pathlib import Path

from core.constants import ND
from core.pipelines.stage import Stage
from core.utils.municipalities import get_region, get_same_region
from pipelines.gobierno_y_seguridad.helpers.aggregate import aggregate
from pipelines.gobierno_y_seguridad.helpers.ranking import rank
from pipelines.gobierno_y_seguridad.helpers.region import filter_region

MAPA_PLACEHOLDER = Path("templates/assets/mapa_placeholder.png")

MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


def _fmt(value, decimals=2) -> str:
    if value is None:
        return ND
    return f"{round(value, decimals):,.{decimals}f}".replace(",", r"\,")


def _fmt_int(value) -> str:
    if value is None:
        return ND
    return f"{int(value):,}".replace(",", r"\,")


def _grafica_placeholder(caption: str) -> str:
    return (
        "\\begin{figure}[H]\n"
        "\\centering\n"
        f"\\caption{{\\textbf{{{caption}}}}}\n"
        f"\\includegraphics[width=\\textwidth]{{{MAPA_PLACEHOLDER}}}\n"
        "\\end{figure}"
    )


def _process_participacion(participacion, municipio_id):
    cve_mun = int(municipio_id)

    anios = sorted({r["anio"] for r in participacion}, reverse=True)
    anio_ultimo = anios[0] if len(anios) >= 1 else 2024
    anio_penultimo = anios[1] if len(anios) >= 2 else 2021
    anio_antepenultimo = anios[2] if len(anios) >= 3 else 2018

    by_anio = {}
    for r in participacion:
        by_anio.setdefault(r["anio"], {})[r["municipio_id"]] = r

    def _rank_anio(anio):
        entries = by_anio.get(anio, {})
        ranked = sorted(entries.values(), key=lambda x: x["pct"], reverse=True)
        return {r["municipio_id"]: i + 1 for i, r in enumerate(ranked)}

    ranks = {
        a: _rank_anio(a) for a in [anio_antepenultimo, anio_penultimo, anio_ultimo]
    }

    mun_data = {}
    for r in participacion:
        if r["municipio_id"] == cve_mun:
            mun_data[r["anio"]] = r

    ctx = {}
    ctx["gs_anio_elecciones"] = anio_ultimo
    ctx["gs_penultimo_anio_eleccion"] = anio_penultimo
    ctx["gs_antepenultimo_anio_eleccion"] = anio_antepenultimo

    d = mun_data.get(anio_ultimo)
    ctx["gs_porcentaje_participacion_electoral"] = _fmt(d["pct"]) if d else ND
    ctx["gs_posicion_eleccion"] = ranks[anio_ultimo].get(cve_mun, ND)

    d = mun_data.get(anio_penultimo)
    ctx["gs_porcentaje_participacion_penultimo_anio_eleccion"] = (
        _fmt(d["pct"]) if d else ND
    )
    ctx["gs_posicion_participacion_penultimo_anio_eleccion"] = ranks[
        anio_penultimo
    ].get(cve_mun, ND)

    d = mun_data.get(anio_antepenultimo)
    ctx["gs_porcentaje_participacion_antepenultimo_anio_eleccion"] = (
        _fmt(d["pct"]) if d else ND
    )
    ctx["gs_posicion_participacion_antepenultimo_anio_eleccion"] = ranks[
        anio_antepenultimo
    ].get(cve_mun, ND)

    region_munis = get_same_region(str(cve_mun))
    table_rows = []
    for m in sorted(region_munis, key=lambda x: int(x["id"])):
        mid = int(m["id"])
        row = {
            "clave": m["id"],
            "municipio": m["municipio"],
            "es_objetivo": mid == cve_mun,
        }
        for anio, prefix in [
            (anio_antepenultimo, "antepenultimo"),
            (anio_penultimo, "penultimo"),
            (anio_ultimo, "ultimo"),
        ]:
            entry = by_anio.get(anio, {}).get(mid)
            row[f"pct_{prefix}"] = _fmt(entry["pct"]) if entry else ND
            row[f"pos_{prefix}"] = ranks[anio].get(mid, ND)
        table_rows.append(row)
    table_rows.sort(key=lambda r: (0 if r["es_objetivo"] else 1, r["clave"]))

    ctx["gs_tabla_participacion"] = table_rows
    return ctx


def _build_ingresos_table(municipio_id: str) -> list[dict]:
    region_munis = get_same_region(municipio_id)
    cvegeo_objetivo = f"14{int(municipio_id):03d}"
    rows = []
    for m in sorted(region_munis, key=lambda x: int(x["id"])):
        cvegeo = f"14{int(m['id']):03d}"
        rows.append(
            {
                "clave": m["id"],
                "municipio": m["municipio"],
                "pct_ing_ant": ND,
                "pos_ing_ant": ND,
                "pct_ing_act": ND,
                "pos_ing_act": ND,
                "pc_ant": ND,
                "pos_pc_ant": ND,
                "pc_act": ND,
                "pos_pc_act": ND,
                "es_objetivo": cvegeo == cvegeo_objetivo,
            }
        )
    rows.sort(key=lambda r: (0 if r["es_objetivo"] else 1, r["clave"]))
    return rows


def _process_incidencia(carpetas_por_mes, casos_bien_afectado, casos_por_delito):
    ctx = {}

    if not carpetas_por_mes:
        ctx["gs_mes_inicio_periodo_incidencia_delictiva"] = ND
        ctx["gs_anio_inicio_periodo_incidencia_delictiva"] = ND
        ctx["gs_mes_fin_periodo_incidencia_delictiva"] = ND
        ctx["gs_anio_fin_periodo_incidencia_delictiva"] = ND
        ctx["gs_total_carpetas_abiertas"] = ND
        ctx["gs_carpetas_aperturadas_primer_anio"] = ND
        ctx["gs_carpetas_aperturadas_segundo_anio"] = ND
        ctx["gs_mes_mas_casos"] = ND
        ctx["gs_total_carpetas_mes_mas_casos"] = ND
        ctx["gs_mes_menos_casos"] = ND
        ctx["gs_total_carpetas_mes_menos_casos"] = ND
        ctx["gs_promedio_carpetas_abiertas_por_mes"] = ND
    else:
        years = sorted({int(r["anio"]) for r in carpetas_por_mes})
        anio_inicio = years[0]
        anio_fin = years[-1]
        meses_inicio = [r for r in carpetas_por_mes if int(r["anio"]) == anio_inicio]
        meses_fin = [r for r in carpetas_por_mes if int(r["anio"]) == anio_fin]

        primer_mes = min(meses_inicio, key=lambda r: int(r["mes"]))
        ultimo_mes = max(meses_fin, key=lambda r: int(r["mes"]))

        ctx["gs_mes_inicio_periodo_incidencia_delictiva"] = MESES.get(
            int(primer_mes["mes"]), ND
        )
        ctx["gs_anio_inicio_periodo_incidencia_delictiva"] = anio_inicio
        ctx["gs_mes_fin_periodo_incidencia_delictiva"] = MESES.get(
            int(ultimo_mes["mes"]), ND
        )
        ctx["gs_anio_fin_periodo_incidencia_delictiva"] = anio_fin

        total = sum(r["total"] for r in carpetas_por_mes)
        ctx["gs_total_carpetas_abiertas"] = _fmt_int(total)

        total_primer = sum(r["total"] for r in meses_inicio)
        total_segundo = sum(r["total"] for r in meses_fin)
        ctx["gs_carpetas_aperturadas_primer_anio"] = _fmt_int(total_primer)
        ctx["gs_carpetas_aperturadas_segundo_anio"] = _fmt_int(total_segundo)

        mes_max = max(carpetas_por_mes, key=lambda r: r["total"])
        mes_min = min(carpetas_por_mes, key=lambda r: r["total"])
        ctx["gs_mes_mas_casos"] = (
            f"{MESES.get(int(mes_max['mes']), ND)} {int(mes_max['anio'])}"
        )
        ctx["gs_total_carpetas_mes_mas_casos"] = _fmt_int(mes_max["total"])
        ctx["gs_mes_menos_casos"] = (
            f"{MESES.get(int(mes_min['mes']), ND)} {int(mes_min['anio'])}"
        )
        ctx["gs_total_carpetas_mes_menos_casos"] = _fmt_int(mes_min["total"])

        promedio = total / len(carpetas_por_mes)
        ctx["gs_promedio_carpetas_abiertas_por_mes"] = _fmt(promedio)

    if not casos_bien_afectado:
        ctx["gs_principal_bien_juridico_afectado"] = ND
        ctx["gs_porcentaje_principal_bien_juridico_afectado"] = ND
        ctx["gs_segundo_bien_juridico_afectado"] = ND
        ctx["gs_porcentaje_segundo_bien_juridico_afectado"] = ND
        ctx["gs_tercer_bien_juridico_afectado"] = ND
        ctx["gs_porcentaje_tercer_bien_juridico_afectado"] = ND
    else:
        total_bienes = sum(r["total"] for r in casos_bien_afectado)
        for i, prefix in enumerate(["principal", "segundo", "tercer"]):
            if i < len(casos_bien_afectado):
                bien = casos_bien_afectado[i]
                pct = bien["total"] / total_bienes * 100 if total_bienes else 0
                ctx[f"gs_{prefix}_bien_juridico_afectado"] = bien["bien_afectado"]
                ctx[f"gs_porcentaje_{prefix}_bien_juridico_afectado"] = _fmt(pct)
            else:
                ctx[f"gs_{prefix}_bien_juridico_afectado"] = ND
                ctx[f"gs_porcentaje_{prefix}_bien_juridico_afectado"] = ND

    if not casos_por_delito:
        ctx["gs_principal_delito_con_mas_carpetas"] = ND
        ctx["gs_total_carpetas_principal_delito"] = ND
        ctx["gs_segundo_delito_con_mas_carpetas"] = ND
        ctx["gs_total_carpetas_segundo_delito"] = ND
        ctx["gs_tercer_delito_con_mas_carpetas"] = ND
        ctx["gs_total_carpetas_tercer_delito"] = ND
    else:
        labels = ["principal", "segundo", "tercer"]
        for i, label in enumerate(labels):
            if i < len(casos_por_delito):
                d = casos_por_delito[i]
                ctx[f"gs_{label}_delito_con_mas_carpetas"] = d["delito"]
                ctx[f"gs_total_carpetas_{label}_delito"] = _fmt_int(d["total"])
            else:
                ctx[f"gs_{label}_delito_con_mas_carpetas"] = ND
                ctx[f"gs_total_carpetas_{label}_delito"] = ND

    return ctx


class Analizer(Stage):
    def __init__(self, municipio_id: str):
        self.municipio_id = municipio_id

    def execute(self, input_data: dict) -> dict:
        conteo = input_data["conteo_municipio_anio"]
        carpetas_por_mes = input_data["carpetas_por_mes"]
        casos_bien_afectado = input_data["casos_bien_afectado"]
        casos_por_delito = input_data["casos_por_delito"]
        participacion = input_data["participacion"]
        anio_actual = input_data["anio_actual"]
        anio_anterior = input_data["anio_anterior"]

        cve_mun = int(self.municipio_id)
        mun_id = str(cve_mun)

        munis = aggregate(conteo, anio_anterior, anio_actual)
        rank(munis)
        region = filter_region(munis, mun_id)

        cvegeo_objetivo = f"14{cve_mun:03d}"
        nombre = next(
            (m["municipio"] for m in munis if m["cvegeo"] == cvegeo_objetivo),
            None,
        )
        if not nombre:
            region_munis = get_same_region(mun_id)
            nombre = next(
                (m["municipio"] for m in region_munis if m["id"] == mun_id),
                mun_id,
            )

        mun_data = next((m for m in munis if m["cvegeo"] == cvegeo_objetivo), None)

        ctx = {}
        ctx["gs_municipio_nombre"] = nombre
        ctx["gs_region_nombre"] = get_region(mun_id)
        ctx["gs_region"] = get_region(mun_id)
        ctx["gs_municipio_clave"] = cvegeo_objetivo
        ctx["gs_anio_anterior"] = anio_anterior
        ctx["gs_anio_actual"] = anio_actual
        ctx["gs_tabla_delitos"] = region

        ctx["gs_anio_acumulado_seguridad"] = anio_actual
        ctx["gs_anio_anterior_acumulado_seguridad"] = anio_anterior
        ctx["gs_anio_pasado_seguridad"] = anio_anterior
        ctx["gs_anio_seguridad"] = anio_actual

        if mun_data:
            ctx["gs_tasa_delitos"] = _fmt(mun_data["valor_actual"])
            ctx["gs_posicion_estado_delitos"] = mun_data.get("lugar_actual", ND)
            ctx["gs_tasa_delitos_anio_anterior"] = _fmt(mun_data["valor_anterior"])
            ctx["gs_posicion_estatal_delitos_anio_anterior"] = mun_data.get(
                "lugar_anterior", ND
            )
            ctx["gs_variacion_porcentual_seguridad"] = _fmt(mun_data["variacion"])
            ctx["gs_posicion_variacion_seguridad"] = mun_data.get("lugar_variacion", ND)
        else:
            ctx["gs_tasa_delitos"] = ND
            ctx["gs_posicion_estado_delitos"] = ND
            ctx["gs_tasa_delitos_anio_anterior"] = ND
            ctx["gs_posicion_estatal_delitos_anio_anterior"] = ND
            ctx["gs_variacion_porcentual_seguridad"] = ND
            ctx["gs_posicion_variacion_seguridad"] = ND

        participacion_ctx = _process_participacion(participacion, mun_id)
        ctx.update(participacion_ctx)

        ctx["gs_anio_efipem"] = 2023
        ctx["gs_anio_anterior_efipem"] = 2022
        ctx["gs_anio_anterior_porcentaje_ingresos_per_capita"] = 2022
        ctx["gs_anio_anterior_ingreso_per_capita"] = 2022
        ctx["gs_porcentaje_ingresos_propios_respecto_total"] = ND
        ctx["gs_posicion_nivel_estado_ingresos_per_capita_porcentaje"] = ND
        ctx["gs_anio_anterior_porcentaje_ingresos_propios_respecto_total"] = ND
        ctx["gs_anio_anterior_posicion_nivel_estado_ingresos_per_capita"] = ND
        ctx["gs_valor_ingresos_per_capita"] = ND
        ctx["gs_posicion_estatal_ingreso_per_capita"] = ND
        ctx["gs_anio_anterior_valor_ingreso_per_capita"] = ND
        ctx["gs_posicion_anio_anterior_ingreso_percapita"] = ND
        ctx["gs_tabla_ingresos"] = _build_ingresos_table(mun_id)

        incidencia_ctx = _process_incidencia(
            carpetas_por_mes, casos_bien_afectado, casos_por_delito
        )
        ctx.update(incidencia_ctx)

        ctx["gs_grafica_carpetas_de_investigacion_por_mes"] = _grafica_placeholder(
            f"Carpetas de investigación abiertas por mes. {nombre}"
        )
        ctx["gs_grafica_distribucion_porcentual_bienes_juridicos_afectados"] = (
            _grafica_placeholder(
                f"Distribución porcentual de bienes jurídicos afectados. {nombre}"
            )
        )
        ctx["gs_grafica_carpetas_cinco_principales_delitos"] = _grafica_placeholder(
            f"Carpetas de investigación por los cinco principales delitos. {nombre}"
        )

        return ctx
