from pathlib import Path

from core.constants import DASH, ND
from core.pipelines.stage import Stage
from core.utils.logger import Logger
from core.utils.municipalities import get_same_region
from pipelines.gobierno_y_seguridad.charts.incidencia import (
    grafica_bienes_juridicos,
    grafica_carpetas_por_mes,
    grafica_principales_delitos,
)
from pipelines.gobierno_y_seguridad.helpers.aggregate import aggregate
from pipelines.gobierno_y_seguridad.helpers.ranking import rank
from pipelines.gobierno_y_seguridad.helpers.region import filter_region

MAPA_PLACEHOLDER = Path("templates/assets/mapa_placeholder.png")
CHARTS_DIR = Path("output/charts")

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


def _grafica_latex(path, num, titulo, fuente):
    return (
        "\\begin{figure}[H]\n"
        f"{{\\color{{colorTexto}}Gráfica {num}}}\\\\\n"
        f"{{\\color{{colorTexto}}\\textbf{{{titulo}}}}}\n"
        "\\vspace{0.3cm}\n\n"
        f"\\includegraphics[width=0.95\\textwidth]{{{path}}}\n\n"
        f"{{\\footnotesize {fuente}}}\n"
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
            "clave": f"14{mid:03d}",
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


CONCEPTOS_PROPIOS = {
    "Impuestos",
    "Cuotas y Aportaciones de Seguridad Social",
    "Contribuciones de Mejoras",
    "Derechos",
    "Productos",
    "Aprovechamientos",
}


def _build_ingresos_por_municipio(ingresos_raw):
    data = {}
    for r in ingresos_raw:
        key = (r["cvegeo"], r["anio"])
        entry = data.setdefault(
            key, {"total": 0, "propios": 0, "cve_mun": r["cve_mun"], "anio": r["anio"]}
        )
        if r["clasificador"] == "Tema":
            entry["total"] = r["valor"]
        elif r["concepto"] in CONCEPTOS_PROPIOS:
            entry["propios"] += r["valor"]
    return data


def _rank_metric(data, anio, metric_fn):
    entries = [
        (cvegeo, metric_fn(v))
        for (cvegeo, a), v in data.items()
        if a == anio and metric_fn(v) is not None
    ]
    entries.sort(key=lambda x: x[1], reverse=True)
    return {cvegeo: pos + 1 for pos, (cvegeo, _) in enumerate(entries)}


def _process_ingresos(
    ingresos_raw, poblacion, municipio_id, anio_efipem, anio_anterior_efipem
):
    ctx = {}
    cve_mun = int(municipio_id)
    cvegeo_objetivo = f"14{cve_mun:03d}"

    if not ingresos_raw or not anio_efipem:
        return None

    pob_map = {(r["cve_mun"], r["anio"]): r["total"] for r in poblacion}
    data = _build_ingresos_por_municipio(ingresos_raw)

    def pct_propios(v):
        return v["propios"] / v["total"] * 100 if v["total"] else None

    def per_capita(v):
        pob = pob_map.get((v["cve_mun"], v["anio"]))
        return v["total"] / pob if pob else None

    rank_pct_act = _rank_metric(data, anio_efipem, pct_propios)
    rank_pct_ant = _rank_metric(data, anio_anterior_efipem, pct_propios)
    rank_pc_act = _rank_metric(data, anio_efipem, per_capita)
    rank_pc_ant = _rank_metric(data, anio_anterior_efipem, per_capita)

    ctx["gs_anio_efipem"] = anio_efipem
    ctx["gs_anio_anterior_efipem"] = anio_anterior_efipem
    ctx["gs_anio_anterior_porcentaje_ingresos_per_capita"] = anio_anterior_efipem
    ctx["gs_anio_anterior_ingreso_per_capita"] = anio_anterior_efipem

    mun_act = data.get((cvegeo_objetivo, anio_efipem))
    mun_ant = data.get((cvegeo_objetivo, anio_anterior_efipem))

    if mun_act and mun_act["total"]:
        pct_act = pct_propios(mun_act)
        ctx["gs_porcentaje_ingresos_propios_respecto_total"] = _fmt(pct_act)
        ctx["gs_posicion_nivel_estado_ingresos_per_capita_porcentaje"] = (
            rank_pct_act.get(cvegeo_objetivo, DASH)
        )
        pc_act = per_capita(mun_act)
        ctx["gs_valor_ingresos_per_capita"] = _fmt(pc_act) if pc_act else DASH
        ctx["gs_posicion_estatal_ingreso_per_capita"] = rank_pc_act.get(
            cvegeo_objetivo, DASH
        )
    else:
        ctx["gs_porcentaje_ingresos_propios_respecto_total"] = DASH
        ctx["gs_posicion_nivel_estado_ingresos_per_capita_porcentaje"] = DASH
        ctx["gs_valor_ingresos_per_capita"] = DASH
        ctx["gs_posicion_estatal_ingreso_per_capita"] = DASH

    if mun_ant and mun_ant["total"]:
        pct_ant = pct_propios(mun_ant)
        ctx["gs_anio_anterior_porcentaje_ingresos_propios_respecto_total"] = _fmt(
            pct_ant
        )
        ctx["gs_anio_anterior_posicion_nivel_estado_ingresos_per_capita"] = (
            rank_pct_ant.get(cvegeo_objetivo, DASH)
        )
        pc_ant = per_capita(mun_ant)
        ctx["gs_anio_anterior_valor_ingreso_per_capita"] = (
            _fmt(pc_ant) if pc_ant else DASH
        )
        ctx["gs_posicion_anio_anterior_ingreso_percapita"] = rank_pc_ant.get(
            cvegeo_objetivo, DASH
        )
    else:
        ctx["gs_anio_anterior_porcentaje_ingresos_propios_respecto_total"] = DASH
        ctx["gs_anio_anterior_posicion_nivel_estado_ingresos_per_capita"] = DASH
        ctx["gs_anio_anterior_valor_ingreso_per_capita"] = DASH
        ctx["gs_posicion_anio_anterior_ingreso_percapita"] = DASH

    region_munis = get_same_region(municipio_id)
    table_rows = []
    for m in sorted(region_munis, key=lambda x: int(x["id"])):
        mid = int(m["id"])
        cvegeo = f"14{mid:03d}"
        row = {
            "clave": cvegeo,
            "municipio": m["municipio"],
            "es_objetivo": cvegeo == cvegeo_objetivo,
        }

        for anio, suffix, rank_pct, rank_pc in [
            (anio_anterior_efipem, "ant", rank_pct_ant, rank_pc_ant),
            (anio_efipem, "act", rank_pct_act, rank_pc_act),
        ]:
            entry = data.get((cvegeo, anio))
            if entry and entry["total"]:
                pct = pct_propios(entry)
                pc = per_capita(entry)
                row[f"pct_ing_{suffix}"] = _fmt(pct) if pct is not None else DASH
                row[f"pos_ing_{suffix}"] = rank_pct.get(cvegeo, DASH)
                row[f"pc_{suffix}"] = _fmt(pc) if pc is not None else DASH
                row[f"pos_pc_{suffix}"] = rank_pc.get(cvegeo, DASH)
            else:
                row[f"pct_ing_{suffix}"] = DASH
                row[f"pos_ing_{suffix}"] = DASH
                row[f"pc_{suffix}"] = DASH
                row[f"pos_pc_{suffix}"] = DASH

        table_rows.append(row)
    table_rows.sort(key=lambda r: (0 if r["es_objetivo"] else 1, r["clave"]))

    ctx["gs_tabla_ingresos"] = table_rows
    return ctx


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
        Logger.info("Gobierno y Seguridad: procesando indicadores")
        conteo = input_data["conteo_municipio_anio"]
        carpetas_por_mes = input_data["carpetas_por_mes"]
        casos_bien_afectado = input_data["casos_bien_afectado"]
        casos_por_delito = input_data["casos_por_delito"]
        participacion = input_data["participacion"]
        anio_actual = input_data["anio_actual"]
        anio_anterior = input_data["anio_anterior"]

        cve_mun = int(self.municipio_id)
        mun_id = str(cve_mun)

        poblacion = input_data.get("poblacion", [])
        pob_map = {(r["cve_mun"], r["anio"]): r["total"] for r in poblacion}

        munis = aggregate(conteo, anio_anterior, anio_actual, pob_map)
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
        ctx["gs_municipio_clave"] = cvegeo_objetivo
        ctx["gs_anio_anterior"] = anio_anterior
        ctx["gs_anio_actual"] = anio_actual
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

        for row in region:
            row["valor_anterior"] = _fmt(row["valor_anterior"])
            row["valor_actual"] = _fmt(row["valor_actual"])
            row["variacion"] = _fmt(row["variacion"])
        ctx["gs_tabla_delitos"] = region

        if not mun_data:
            ctx["gs_tasa_delitos"] = ND
            ctx["gs_posicion_estado_delitos"] = ND
            ctx["gs_tasa_delitos_anio_anterior"] = ND
            ctx["gs_posicion_estatal_delitos_anio_anterior"] = ND
            ctx["gs_variacion_porcentual_seguridad"] = ND
            ctx["gs_posicion_variacion_seguridad"] = ND

        participacion_ctx = _process_participacion(participacion, mun_id)
        ctx.update(participacion_ctx)

        ingresos_raw = input_data.get("ingresos_raw", [])
        anio_efipem = input_data.get("anio_efipem")
        anio_anterior_efipem = input_data.get("anio_anterior_efipem")

        ingresos_ctx = _process_ingresos(
            ingresos_raw, poblacion, mun_id, anio_efipem, anio_anterior_efipem
        )
        if ingresos_ctx:
            ctx.update(ingresos_ctx)
        else:
            ctx["gs_anio_efipem"] = ND
            ctx["gs_anio_anterior_efipem"] = ND
            ctx["gs_anio_anterior_porcentaje_ingresos_per_capita"] = ND
            ctx["gs_anio_anterior_ingreso_per_capita"] = ND
            ctx["gs_porcentaje_ingresos_propios_respecto_total"] = ND
            ctx["gs_posicion_nivel_estado_ingresos_per_capita_porcentaje"] = ND
            ctx["gs_anio_anterior_porcentaje_ingresos_propios_respecto_total"] = ND
            ctx["gs_anio_anterior_posicion_nivel_estado_ingresos_per_capita"] = ND
            ctx["gs_valor_ingresos_per_capita"] = ND
            ctx["gs_posicion_estatal_ingreso_per_capita"] = ND
            ctx["gs_anio_anterior_valor_ingreso_per_capita"] = ND
            ctx["gs_posicion_anio_anterior_ingreso_percapita"] = ND
            ctx["gs_tabla_ingresos"] = []

        incidencia_ctx = _process_incidencia(
            carpetas_por_mes, casos_bien_afectado, casos_por_delito
        )
        ctx.update(incidencia_ctx)

        fuente_sesnsp = (
            "Elaborado por el IIEG con datos del Secretariado "
            "Ejecutivo del Sistema Nacional de Seguridad Pública."
        )
        mun_id_str = str(cve_mun)

        if carpetas_por_mes:
            sorted_carp = sorted(carpetas_por_mes, key=lambda r: (r["anio"], r["mes"]))
            p_ini = sorted_carp[0]
            p_fin = sorted_carp[-1]
            periodo = (
                f"en el municipio de {nombre} desde "
                f"{MESES[p_ini['mes']]} {p_ini['anio']} "
                f"a {MESES[p_fin['mes']]} {p_fin['anio']}"
            )

            chart_path = CHARTS_DIR / mun_id_str / "gs_carpetas_mes.png"
            grafica_carpetas_por_mes(carpetas_por_mes, nombre, chart_path)
            ctx["gs_grafica_carpetas_de_investigacion_por_mes"] = _grafica_latex(
                chart_path,
                1,
                f"Cantidad de carpetas de investigación por mes, {periodo}",
                fuente_sesnsp,
            )
        else:
            ctx["gs_grafica_carpetas_de_investigacion_por_mes"] = _grafica_placeholder(
                f"Carpetas de investigación abiertas por mes. {nombre}"
            )
            periodo = nombre

        if casos_bien_afectado:
            chart_path = CHARTS_DIR / mun_id_str / "gs_bienes_juridicos.png"
            grafica_bienes_juridicos(casos_bien_afectado, nombre, chart_path)
            ctx["gs_grafica_distribucion_porcentual_bienes_juridicos_afectados"] = (
                _grafica_latex(
                    chart_path,
                    2,
                    "Distribución porcentual de los bienes jurídicos "
                    f"afectados, {periodo}",
                    fuente_sesnsp,
                )
            )
        else:
            ctx["gs_grafica_distribucion_porcentual_bienes_juridicos_afectados"] = (
                _grafica_placeholder(
                    f"Distribución porcentual de bienes jurídicos afectados. {nombre}"
                )
            )

        if casos_por_delito:
            chart_path = CHARTS_DIR / mun_id_str / "gs_principales_delitos.png"
            grafica_principales_delitos(
                casos_por_delito,
                nombre,
                chart_path,
            )
            ctx["gs_grafica_carpetas_cinco_principales_delitos"] = _grafica_latex(
                chart_path,
                3,
                "Cantidad de carpetas por los 5 principales subtipos de delitos, "
                f"{periodo}",
                fuente_sesnsp,
            )
        else:
            ctx["gs_grafica_carpetas_cinco_principales_delitos"] = _grafica_placeholder(
                f"Carpetas de investigación por los cinco principales delitos. {nombre}"
            )

        Logger.info("Gobierno y Seguridad: análisis completo")
        return ctx
