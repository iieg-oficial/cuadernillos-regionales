from pathlib import Path

from core.constants import DASH, INCOMPLETE_AGRICOLA, INCOMPLETE_PECUARIA, ND
from core.pipelines.stage import Stage
from core.utils.helpers import rows_have_na
from core.utils.logger import Logger
from core.utils.municipalities import get_same_region, get_same_region_ids
from pipelines.economia.charts.produccion import grafica_produccion
from pipelines.economia.helpers.vacb import (
    build_mayor_crecimiento_text,
    build_subsectores_text,
)

MAPA_PLACEHOLDER = (
    "\\includegraphics[width=\\textwidth]{templates/assets/mapa_placeholder.png}"
)

CHARTS_DIR = Path("output/charts")

ANIO_CE = 2024
ANIO_CE_ANTERIOR = 2019

RANGOS_ORDEN = [
    "0 a 5 personas",
    "6 a 10 personas",
    "11 a 30 personas",
    "31 a 50 personas",
    "51 a 100 personas",
    "101 a 250 personas",
    "251 y más personas",
]

RANGO_KEYS = ["r0a5", "r6a10", "r11a30", "r31a50", "r51a100", "r101a250", "r251mas"]


def _fmt(value, decimals=2) -> str:
    if value is None:
        return ND
    return f"{round(value, decimals):,.{decimals}f}".replace(",", r"\,")


def _fmt_int(value) -> str:
    if value is None:
        return ND
    return f"{int(value):,}".replace(",", r"\,")


def _pct(value) -> str:
    if value is None:
        return ND
    return f"{value:,.2f}".replace(",", r"\,") + r"\,\%"


def _grafica_latex(path, municipio, tipo, datos):
    n = min(6, len(datos))
    ultimos = datos[-n:]
    anio_ini = ultimos[0]["anio"]
    anio_fin = ultimos[-1]["anio"]
    titulo = (
        f"Valor de la producción {tipo} de "
        f"{municipio}, {anio_ini}-{anio_fin} (millones de pesos)"
    )
    return (
        "\\begin{figure}[H]\n"
        "\\refstepcounter{grafica}%\n"
        "{\\color{colorTexto}Gráfica \\thegrafica}\\\\\n"
        f"{{\\color{{colorTexto}}\\textbf{{{titulo}}}}}\n"
        "\\vspace{0.3cm}\n\n"
        f"\\includegraphics[width=0.95\\textwidth]{{{path}}}\n"
        "\\end{figure}\n"
        "\\vspace{-10pt}\\noindent{\\footnotesize Fuente: SAGARPA. "
        f"Datos abiertos de la DGSIAP, {anio_ini}--{anio_fin}.}}"
    )


def _build_denue_table(unidades_sector_rango):
    sector_data = {}
    for row in unidades_sector_rango:
        sector = row["sector"]
        rango = row["rango_personal"]
        total = row["total"]
        if sector not in sector_data:
            sector_data[sector] = {k: 0 for k in RANGO_KEYS}
            sector_data[sector]["total"] = 0
        for i, rango_desc in enumerate(RANGOS_ORDEN):
            if (
                rango_desc.lower() in rango.lower()
                or rango.lower() in rango_desc.lower()
            ):
                sector_data[sector][RANGO_KEYS[i]] += total
                break
        sector_data[sector]["total"] += total

    grand_total = sum(v["total"] for v in sector_data.values())

    rows = []
    for sector, datos in sorted(sector_data.items()):
        t = datos["total"]
        rows.append(
            {
                "sector": sector,
                "r0a5": _fmt_int(datos["r0a5"]) if datos["r0a5"] else "0",
                "r6a10": _fmt_int(datos["r6a10"]) if datos["r6a10"] else "0",
                "r11a30": _fmt_int(datos["r11a30"]) if datos["r11a30"] else "0",
                "r31a50": _fmt_int(datos["r31a50"]) if datos["r31a50"] else "0",
                "r51a100": _fmt_int(datos["r51a100"]) if datos["r51a100"] else "0",
                "r101a250": _fmt_int(datos["r101a250"]) if datos["r101a250"] else "0",
                "r251mas": _fmt_int(datos["r251mas"]) if datos["r251mas"] else "0",
                "total": _fmt_int(t),
                "pct_total": _fmt(t / grand_total * 100) if grand_total else ND,
            }
        )
    return rows, grand_total, sector_data


def _top_sectores(sector_data, grand_total):
    sorted_sectors = sorted(
        sector_data.items(), key=lambda x: x[1]["total"], reverse=True
    )
    result = []
    for sector, datos in sorted_sectors[:3]:
        t = datos["total"]
        result.append(
            {
                "sector": sector,
                "pct": _pct(t / grand_total * 100) if grand_total else ND,
            }
        )
    while len(result) < 3:
        result.append({"sector": ND, "pct": ND})
    return result


def _build_vacb_table(
    vacb_actual, vacb_anterior, vacb_total_actual, vacb_total_anterior, factor
):
    anterior_by_codigo = {r["codigo"]: r["vacb"] for r in vacb_anterior}

    top_actual = vacb_actual[:9]
    rows = []
    for r in top_actual:
        sub = r["subsector"]
        vact = r["vacb"]
        vact_real = vact * factor if (vact is not None and factor) else None
        vant = anterior_by_codigo.get(r["codigo"])
        pct_part = _fmt(vact / vacb_total_actual * 100) if vacb_total_actual else ND
        if vant and vact_real is not None:
            var_str = _fmt((vact_real - vant) / vant * 100)
        else:
            var_str = DASH
        rows.append(
            {
                "subsector": sub,
                "vacb_anterior": _fmt(vant, 2) if vant else _fmt(0),
                "vacb_actual": _fmt(vact, 2) if vact else ND,
                "vacb_real": _fmt(vact_real, 2) if vact_real is not None else ND,
                "pct_part": pct_part,
                "var_pct": var_str,
            }
        )

    if len(vacb_actual) > 9:
        top9_actual = sum(r["vacb"] for r in top_actual if r["vacb"])
        top9_anterior = sum(
            anterior_by_codigo.get(r["codigo"]) or 0 for r in top_actual
        )
        otros_act = (
            vacb_total_actual - top9_actual if vacb_total_actual is not None else None
        )
        otros_act_real = (
            otros_act * factor if (otros_act is not None and factor) else None
        )
        otros_ant = (
            vacb_total_anterior - top9_anterior
            if vacb_total_anterior is not None
            else None
        )
        pct_otros = (
            _fmt(otros_act / vacb_total_actual * 100)
            if (vacb_total_actual and otros_act is not None)
            else ND
        )
        if otros_ant and otros_act_real:
            var_otros = _fmt((otros_act_real - otros_ant) / otros_ant * 100)
        else:
            var_otros = DASH
        rows.append(
            {
                "subsector": "Otros",
                "vacb_anterior": _fmt(otros_ant, 2) if otros_ant else _fmt(0),
                "vacb_actual": _fmt(otros_act, 2) if otros_act else ND,
                "vacb_real": _fmt(otros_act_real, 2)
                if otros_act_real is not None
                else ND,
                "pct_part": pct_otros,
                "var_pct": var_otros,
            }
        )

    return rows


def _norm_grupo(nombre):
    return nombre.lower().replace("ind eléctrica", "ind. eléctrica")


def _cap_grupo(nombre):
    s = _norm_grupo(nombre)
    return s[:1].upper() + s[1:]


def _build_imss_grupos(divisiones, total_t0):
    rows = []
    for d in divisiones:
        t0, t1, t2 = d["t0"], d["t1"], d["t2"]
        pct = _fmt(t0 / total_t0 * 100) if total_t0 else ND
        if t1:
            var_nom = t0 - t1
            var_pct_val = var_nom / t1 * 100
            rows.append(
                {
                    "grupo": _cap_grupo(d["division"]),
                    "t2": _fmt_int(t2),
                    "t1": _fmt_int(t1),
                    "t0": _fmt_int(t0),
                    "pct_part": pct,
                    "var_nominal": _fmt_int(var_nom),
                    "var_pct": _fmt(var_pct_val),
                }
            )
        else:
            rows.append(
                {
                    "grupo": _cap_grupo(d["division"]),
                    "t2": _fmt_int(t2),
                    "t1": _fmt_int(t1),
                    "t0": _fmt_int(t0),
                    "pct_part": pct,
                    "var_nominal": DASH,
                    "var_pct": DASH,
                }
            )
    return rows


def _build_imss_region(sorted_region, region_total, names, cvegeo_mun):
    rows = []
    for m in sorted_region:
        if m["cvegeo"] == cvegeo_mun:
            continue
        t0, t1 = m["t0"], m["t1"]
        nombre = names.get(m["cvegeo"], str(m["cvegeo"]))
        pct = _fmt(t0 / region_total * 100) if region_total else ND
        if t1:
            var_nom = t0 - t1
            var_pct_val = var_nom / t1 * 100
            rows.append(
                {
                    "municipio": nombre,
                    "t1": _fmt_int(t1),
                    "total": _fmt_int(t0),
                    "pct_part": pct,
                    "var_nominal": _fmt_int(var_nom),
                    "var_pct": _fmt(var_pct_val),
                }
            )
        else:
            rows.append(
                {
                    "municipio": nombre,
                    "t1": _fmt_int(t1),
                    "total": _fmt_int(t0),
                    "pct_part": pct,
                    "var_nominal": DASH,
                    "var_pct": DASH,
                }
            )
    return rows


class Analizer(Stage):
    def __init__(self, municipio_id: str):
        self.municipio_id = municipio_id

    def execute(self, input_data: dict) -> dict:
        Logger.info("Economía: procesando indicadores")
        cve_mun = input_data["cve_mun"]
        municipio_id_str = str(self.municipio_id)

        ultima_act = input_data["ultima_actualizacion_denue"]
        unidades_sector_rango = input_data["unidades_sector_rango"]
        total_estatal_denue = input_data["total_estatal_denue"]
        ranking_denue = input_data["ranking_denue"]
        anio_ce = input_data["anio_ce"]
        anio_ce_anterior = input_data["anio_ce_anterior"]
        vacb_actual = input_data["vacb_actual"]
        vacb_anterior = input_data["vacb_anterior"]
        vacb_total_actual = input_data["vacb_total_actual"]
        vacb_total_anterior = input_data["vacb_total_anterior"]
        inpc_promedio_actual = input_data.get("inpc_promedio_actual")
        factor_deflactacion = (
            100 / inpc_promedio_actual if inpc_promedio_actual else None
        )
        vacb_total_actual_real = (
            vacb_total_actual * factor_deflactacion
            if (vacb_total_actual and factor_deflactacion)
            else None
        )

        ctx = {}

        ctx["ec_municipio_nombre"] = input_data.get("municipio_nombre") or ND

        if ultima_act:
            mes_nombre = [
                "enero",
                "febrero",
                "marzo",
                "abril",
                "mayo",
                "junio",
                "julio",
                "agosto",
                "septiembre",
                "octubre",
                "noviembre",
                "diciembre",
            ][ultima_act.month - 1]
            ctx["ec_mes_denue_numero_empresas"] = mes_nombre
            ctx["ec_anio_denue"] = ultima_act.year
            ctx["ec_anio_pasado_denue"] = ultima_act.year - 1
        else:
            ctx["ec_mes_denue_numero_empresas"] = ND
            ctx["ec_anio_denue"] = ND
            ctx["ec_anio_pasado_denue"] = ND

        tabla_denue, grand_total, sector_data = _build_denue_table(
            unidades_sector_rango
        )
        ctx["ec_tabla_denue"] = tabla_denue

        ctx["ec_unidades_economicas"] = _fmt_int(grand_total) if grand_total else ND
        ctx["ec_porcentaje_unidades_economicas"] = (
            _pct(grand_total / total_estatal_denue * 100)
            if (grand_total and total_estatal_denue)
            else ND
        )
        ctx["ec_posicion_municipio_establecimientos"] = (
            str(ranking_denue) if ranking_denue else ND
        )

        top3 = _top_sectores(sector_data, grand_total)
        ctx["ec_sector_mayor_unidades"] = top3[0]["sector"].lower()
        ctx["ec_porcentaje_sector_mayor_unidades"] = top3[0]["pct"]
        ctx["ec_sector_segundo_unidades"] = top3[1]["sector"].lower()
        ctx["ec_porcentaje_sector_segundo_unidades"] = top3[1]["pct"]
        ctx["ec_sector_tercer_unidades"] = top3[2]["sector"].lower()
        ctx["ec_porcentaje_sector_tercer_unidades"] = top3[2]["pct"]

        totales_rango = {k: 0 for k in RANGO_KEYS}
        for datos in sector_data.values():
            for k in RANGO_KEYS:
                totales_rango[k] += datos[k]
        ctx["ec_denue_total_r0a5"] = _fmt_int(totales_rango["r0a5"])
        ctx["ec_denue_total_r6a10"] = _fmt_int(totales_rango["r6a10"])
        ctx["ec_denue_total_r11a30"] = _fmt_int(totales_rango["r11a30"])
        ctx["ec_denue_total_r31a50"] = _fmt_int(totales_rango["r31a50"])
        ctx["ec_denue_total_r51a100"] = _fmt_int(totales_rango["r51a100"])
        ctx["ec_denue_total_r101a250"] = _fmt_int(totales_rango["r101a250"])
        ctx["ec_denue_total_r251mas"] = _fmt_int(totales_rango["r251mas"])

        ctx["ec_anio_ce"] = anio_ce - 1
        ctx["ec_anio_ce_anterior"] = anio_ce_anterior - 1
        ctx["ec_anio_publicacion_ce"] = anio_ce
        ctx["ec_anio_publicacion_ce_anterior"] = anio_ce_anterior

        if vacb_total_actual_real and vacb_total_anterior:
            var_vacb = (
                (vacb_total_actual_real - vacb_total_anterior)
                / vacb_total_anterior
                * 100
            )
            ctx["ec_variacion_valor_agregado_censal"] = _pct(var_vacb)
            ctx["ec_variacion_vacb_total"] = _fmt(var_vacb)
        else:
            ctx["ec_variacion_valor_agregado_censal"] = ND
            ctx["ec_variacion_vacb_total"] = ND

        top3_vacb = vacb_actual[:3]

        if top3_vacb and vacb_total_actual_real and factor_deflactacion:
            suma_top3_real = sum(
                r["vacb"] * factor_deflactacion for r in top3_vacb if r["vacb"]
            )
            pct_principales = _pct(suma_top3_real / vacb_total_actual_real * 100)
            aportacion_principales = _fmt(suma_top3_real, 2)
        else:
            pct_principales = ND
            aportacion_principales = ND

        if not top3_vacb:
            Logger.warning(
                f"Economía: municipio {municipio_id_str} sin desglose de VACB por "
                "subsector, usando redacción de confidencialidad"
            )
        elif len(top3_vacb) < 3:
            Logger.warning(
                f"Economía: municipio {municipio_id_str} con solo "
                f"{len(top3_vacb)} subsector(es) de VACB, usando redacción reducida"
            )
        else:
            Logger.info("Economía: VACB con redacción completa de tres subsectores")

        ctx["ec_porcentaje_aportacion_principales_subsectores"] = pct_principales
        ctx["ec_aportacion_principales_subsectores"] = aportacion_principales
        ctx["ec_texto_subsectores_vacb"] = build_subsectores_text(
            [r["subsector"].lower() for r in top3_vacb],
            ctx["ec_municipio_nombre"],
            ctx["ec_anio_ce"],
            pct_principales,
            aportacion_principales,
        )

        anterior_by_codigo2 = {r["codigo"]: r["vacb"] for r in vacb_anterior}
        mayor_crecimiento = None
        mayor_tasa = None
        for r in vacb_actual:
            vact = r["vacb"]
            vact_real = (
                vact * factor_deflactacion if (vact and factor_deflactacion) else None
            )
            vant = anterior_by_codigo2.get(r["codigo"])
            if vact_real and vant:
                tasa = (vact_real - vant) / vant * 100
                if mayor_tasa is None or tasa > mayor_tasa:
                    mayor_tasa = tasa
                    mayor_crecimiento = r

        if mayor_crecimiento:
            sub_mc = mayor_crecimiento["subsector"].lower()
            vact_mc = mayor_crecimiento["vacb"]
            vact_mc_real = (
                vact_mc * factor_deflactacion
                if (vact_mc and factor_deflactacion)
                else None
            )
            vant_mc = anterior_by_codigo2.get(mayor_crecimiento["codigo"])
            ctx["ec_subsector_mayor_crecimiento"] = sub_mc
            ctx["ec_aportacion_anterior_subsector_mayor_crecimiento"] = (
                _fmt(vant_mc, 2) if vant_mc else ND
            )
            ctx["ec_aportacion_subsector_mayor_crecimiento"] = (
                _fmt(vact_mc_real, 2) if vact_mc_real is not None else ND
            )
            ctx["ec_variacion_porcentual_aportacion_subsector_mayor_crecimiento"] = (
                _pct(mayor_tasa) if mayor_tasa is not None else ND
            )
        else:
            ctx["ec_subsector_mayor_crecimiento"] = ND
            ctx["ec_aportacion_anterior_subsector_mayor_crecimiento"] = ND
            ctx["ec_aportacion_subsector_mayor_crecimiento"] = ND
            ctx["ec_variacion_porcentual_aportacion_subsector_mayor_crecimiento"] = ND

        if not mayor_crecimiento:
            Logger.warning(
                f"Economía: municipio {municipio_id_str} sin subsector comparable "
                "entre censos, omitiendo la frase de mayor crecimiento del VACB"
            )

        ctx["ec_texto_mayor_crecimiento_vacb"] = build_mayor_crecimiento_text(
            ctx["ec_subsector_mayor_crecimiento"] if mayor_crecimiento else None,
            ctx["ec_aportacion_anterior_subsector_mayor_crecimiento"],
            ctx["ec_aportacion_subsector_mayor_crecimiento"],
            ctx["ec_variacion_porcentual_aportacion_subsector_mayor_crecimiento"],
            ctx["ec_anio_ce_anterior"],
            ctx["ec_anio_ce"],
        )

        ctx["ec_tabla_vacb"] = _build_vacb_table(
            vacb_actual,
            vacb_anterior,
            vacb_total_actual,
            vacb_total_anterior,
            factor_deflactacion,
        )
        ctx["ec_tabla_vacb_tiene_na"] = rows_have_na(ctx["ec_tabla_vacb"])
        ctx["ec_vacb_total_real"] = (
            _fmt(vacb_total_actual_real, 2)
            if vacb_total_actual_real is not None
            else ND
        )
        ctx["ec_vacb_total_anterior"] = (
            _fmt(vacb_total_anterior, 2) if vacb_total_anterior else ND
        )
        ctx["ec_vacb_total_actual"] = (
            _fmt(vacb_total_actual, 2) if vacb_total_actual else ND
        )

        imss_fecha = input_data.get("imss_fecha_corte")
        imss_mun = input_data.get("imss_asegurados_mun", {})
        imss_estatal = input_data.get("imss_asegurados_estatal", 0)
        imss_divisiones = input_data.get("imss_por_division", [])
        imss_todos = input_data.get("imss_todos_municipios", [])

        if imss_fecha and imss_mun:
            meses = [
                "enero",
                "febrero",
                "marzo",
                "abril",
                "mayo",
                "junio",
                "julio",
                "agosto",
                "septiembre",
                "octubre",
                "noviembre",
                "diciembre",
            ]
            ctx["ec_mes_corte_imss"] = meses[imss_fecha.month - 1]
            ctx["ec_anio_corte_imss"] = imss_fecha.year
            ctx["ec_anio_anterior_corte_imss"] = imss_fecha.year - 1
            ctx["ec_dos_anios_atras_corte_imss"] = imss_fecha.year - 2

            mun_t0 = imss_mun.get("t0", 0)
            mun_t1 = imss_mun.get("t1", 0)
            mun_t2 = imss_mun.get("t2", 0)

            ctx["ec_total_trabajadores_imss"] = _fmt_int(mun_t0)
            ctx["ec_total_trabajadores_imss_t1"] = _fmt_int(mun_t1)
            ctx["ec_total_trabajadores_imss_t2"] = _fmt_int(mun_t2)

            ctx["ec_porcentaje_trabajadores_asegurados_jalisco"] = (
                _pct(mun_t0 / imss_estatal * 100) if imss_estatal else ND
            )

            if mun_t1:
                var_anual = (mun_t0 - mun_t1) / mun_t1 * 100
                ctx["ec_porcentaje_variacion_asegurados"] = _pct(var_anual)
                ctx["ec_var_pct_total_imss"] = _fmt(var_anual)
                ctx["ec_total_var_nominal_imss"] = _fmt_int(mun_t0 - mun_t1)
            else:
                ctx["ec_porcentaje_variacion_asegurados"] = ND
                ctx["ec_var_pct_total_imss"] = ND
                ctx["ec_total_var_nominal_imss"] = ND

            ctx["ec_tabla_imss_grupos"] = _build_imss_grupos(imss_divisiones, mun_t0)
            ctx["ec_tabla_imss_grupos_tiene_na"] = rows_have_na(
                ctx["ec_tabla_imss_grupos"]
            )

            if imss_divisiones:
                top = imss_divisiones[0]
                ctx["ec_grupo_ec_con_mas_empleos"] = _norm_grupo(top["division"])
                ctx["ec_num_trabajadores_grupo_mayor"] = _fmt_int(top["t0"])
                ctx["ec_porcentaje_trabajadores_grupo_mayor"] = (
                    _pct(top["t0"] / mun_t0 * 100) if mun_t0 else ND
                )
            else:
                ctx["ec_grupo_ec_con_mas_empleos"] = ND
                ctx["ec_num_trabajadores_grupo_mayor"] = ND
                ctx["ec_porcentaje_trabajadores_grupo_mayor"] = ND

            region_cvegeos = {
                14000 + int(m) for m in get_same_region_ids(municipio_id_str)
            }
            region_data = [m for m in imss_todos if m["cvegeo"] in region_cvegeos]
            region_total = sum(m["t0"] for m in region_data)

            sorted_region = sorted(region_data, key=lambda x: x["t0"], reverse=True)
            cvegeo_mun = 14000 + cve_mun
            posicion = next(
                (
                    i + 1
                    for i, m in enumerate(sorted_region)
                    if m["cvegeo"] == cvegeo_mun
                ),
                None,
            )
            ctx["ec_posicion_municipio_region"] = str(posicion) if posicion else ND
            ctx["ec_porcentaje_asegurados_region"] = (
                _pct(mun_t0 / region_total * 100) if region_total else ND
            )
            ctx["ec_pct_asegurados_region_tabla"] = (
                _fmt(mun_t0 / region_total * 100) if region_total else ND
            )

            region_names = {
                14000 + int(m["id"]): m["municipio"]
                for m in get_same_region(municipio_id_str)
            }
            ctx["ec_tabla_imss_region"] = _build_imss_region(
                sorted_region, region_total, region_names, cvegeo_mun
            )
            ctx["ec_trabajadores_imss_t1"] = _fmt_int(
                next(
                    (m["t1"] for m in region_data if m["cvegeo"] == cvegeo_mun),
                    0,
                )
            )
            mun_region_t1 = next(
                (m["t1"] for m in region_data if m["cvegeo"] == cvegeo_mun), 0
            )
            if mun_region_t1:
                ctx["ec_var_nominal_imss"] = _fmt_int(mun_t0 - mun_region_t1)
                var_pct_region = (mun_t0 - mun_region_t1) / mun_region_t1 * 100
                ctx["ec_var_pct_imss"] = _pct(var_pct_region)
                ctx["ec_var_pct_imss_tabla"] = _fmt(var_pct_region)
            else:
                ctx["ec_var_nominal_imss"] = ND
                ctx["ec_var_pct_imss"] = ND
                ctx["ec_var_pct_imss_tabla"] = ND
        else:
            ctx["ec_mes_corte_imss"] = ND
            ctx["ec_anio_corte_imss"] = ND
            ctx["ec_anio_anterior_corte_imss"] = ND
            ctx["ec_dos_anios_atras_corte_imss"] = ND
            ctx["ec_total_trabajadores_imss"] = ND
            ctx["ec_total_trabajadores_imss_t1"] = ND
            ctx["ec_total_trabajadores_imss_t2"] = ND
            ctx["ec_porcentaje_trabajadores_asegurados_jalisco"] = ND
            ctx["ec_porcentaje_variacion_asegurados"] = ND
            ctx["ec_var_pct_total_imss"] = ND
            ctx["ec_total_var_nominal_imss"] = ND
            ctx["ec_grupo_ec_con_mas_empleos"] = ND
            ctx["ec_num_trabajadores_grupo_mayor"] = ND
            ctx["ec_porcentaje_trabajadores_grupo_mayor"] = ND
            ctx["ec_tabla_imss_grupos"] = []
            ctx["ec_tabla_imss_grupos_tiene_na"] = False
            ctx["ec_posicion_municipio_region"] = ND
            ctx["ec_porcentaje_asegurados_region"] = ND
            ctx["ec_pct_asegurados_region_tabla"] = ND
            ctx["ec_tabla_imss_region"] = []
            ctx["ec_trabajadores_imss_t1"] = ND
            ctx["ec_var_nominal_imss"] = ND
            ctx["ec_var_pct_imss"] = ND
            ctx["ec_var_pct_imss_tabla"] = ND

        anio_agricola = input_data.get("anio_agricola")
        agricola_anual = input_data.get("agricola_anual", [])
        agricola_mun = input_data.get("agricola_municipal_mdp")
        agricola_est = input_data.get("agricola_estatal_mdp")
        anio_ganadero = input_data.get("anio_ganadero")
        ganadera_anual = input_data.get("ganadera_anual", [])
        ganadera_mun = input_data.get("ganadera_municipal_mdp")
        ganadera_est = input_data.get("ganadera_estatal_mdp")

        anio_corte = anio_agricola or anio_ganadero
        ctx["ec_anio_corte_sagarpa"] = anio_corte if anio_corte else ND

        municipio_nombre = input_data.get("municipio_nombre") or ""

        mun_int = int(municipio_id_str)
        ctx["ec_agricola_activa"] = mun_int not in INCOMPLETE_AGRICOLA
        ctx["ec_pecuaria_activa"] = mun_int not in INCOMPLETE_PECUARIA
        ctx["ec_agropecuario_activa"] = (
            ctx["ec_agricola_activa"] or ctx["ec_pecuaria_activa"]
        )

        if not ctx["ec_agropecuario_activa"]:
            Logger.warning(
                f"Economía: municipio {mun_int} sin datos agropecuarios, "
                "ignorando sección Agricultura y ganadería"
            )
        else:
            if not ctx["ec_agricola_activa"]:
                Logger.warning(
                    f"Economía: municipio {mun_int} sin datos agrícolas, "
                    "ignorando producción agrícola de la sección"
                )
            if not ctx["ec_pecuaria_activa"]:
                Logger.warning(
                    f"Economía: municipio {mun_int} sin datos pecuarios, "
                    "ignorando producción pecuaria de la sección"
                )

        if ctx["ec_agricola_activa"]:
            if agricola_mun is not None:
                ctx["ec_valor_produccion_agricola"] = _fmt(agricola_mun)
            else:
                ctx["ec_valor_produccion_agricola"] = ND

            if agricola_mun and agricola_est:
                ctx["ec_porcentaje_respecto_al_estado_agricola"] = _pct(
                    agricola_mun / agricola_est * 100
                )
            else:
                ctx["ec_porcentaje_respecto_al_estado_agricola"] = ND

            if len(agricola_anual) >= 2:
                chart_path = CHARTS_DIR / municipio_id_str / "ec_agricultura.png"
                grafica_produccion(
                    agricola_anual, municipio_nombre, "agrícola", chart_path
                )
                ctx["ec_grafica_agricultura"] = _grafica_latex(
                    chart_path, municipio_nombre, "agrícola", agricola_anual
                )
            else:
                ctx["ec_grafica_agricultura"] = MAPA_PLACEHOLDER

        if ctx["ec_pecuaria_activa"]:
            if ganadera_mun is not None:
                ctx["ec_valor_produccion_ganado"] = _fmt(ganadera_mun)
            else:
                ctx["ec_valor_produccion_ganado"] = ND

            if ganadera_mun and ganadera_est:
                ctx["ec_porcentaje_respecto_al_estado_ganado"] = _pct(
                    ganadera_mun / ganadera_est * 100
                )
            else:
                ctx["ec_porcentaje_respecto_al_estado_ganado"] = ND

            if len(ganadera_anual) >= 2:
                chart_path = CHARTS_DIR / municipio_id_str / "ec_ganaderia.png"
                grafica_produccion(
                    ganadera_anual, municipio_nombre, "pecuaria", chart_path
                )
                ctx["ec_grafica_ganaderia"] = _grafica_latex(
                    chart_path, municipio_nombre, "pecuaria", ganadera_anual
                )
            else:
                ctx["ec_grafica_ganaderia"] = MAPA_PLACEHOLDER

        Logger.info("Economía: análisis completo")
        return ctx
