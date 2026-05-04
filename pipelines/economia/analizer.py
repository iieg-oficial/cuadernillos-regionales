from core.pipelines.stage import Stage
from core.utils.municipalities import get_region, get_same_region

ND = "\\ND"
MAPA_PLACEHOLDER = (
    "\\includegraphics[width=\\textwidth]{templates/assets/mapa_placeholder.png}"
)

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


def _build_vacb_table(vacb_actual, vacb_anterior, vacb_total_actual):
    anterior_by_codigo = {r["codigo"]: r["vacb"] for r in vacb_anterior}

    top_actual = vacb_actual[:9]
    rows = []
    for r in top_actual:
        sub = r["subsector"]
        vact = r["vacb"]
        vant = anterior_by_codigo.get(r["codigo"])
        pct_part = _fmt(vact / vacb_total_actual * 100) if vacb_total_actual else ND
        if vant and vact is not None:
            var = (vact - vant) / vant * 100
            var_str = _fmt(var)
        else:
            var_str = ND
        rows.append(
            {
                "subsector": sub,
                "vacb_anterior": _fmt(vant, 2) if vant else ND,
                "vacb_actual": _fmt(vact, 2) if vact else ND,
                "pct_part": pct_part,
                "var_pct": var_str,
            }
        )

    if len(vacb_actual) > 9:
        otros_act = sum(r["vacb"] for r in vacb_actual[9:] if r["vacb"])
        top9_codigos = {x["codigo"] for x in vacb_actual[:9]}
        otros_ant = sum(
            r["vacb"]
            for r in vacb_anterior
            if r["codigo"] not in top9_codigos and r["vacb"]
        )
        pct_otros = (
            _fmt(otros_act / vacb_total_actual * 100) if vacb_total_actual else ND
        )
        if otros_ant and otros_act:
            var_otros = _fmt((otros_act - otros_ant) / otros_ant * 100)
        else:
            var_otros = ND
        rows.append(
            {
                "subsector": "Otros",
                "vacb_anterior": _fmt(otros_ant, 2) if otros_ant else ND,
                "vacb_actual": _fmt(otros_act, 2) if otros_act else ND,
                "pct_part": pct_otros,
                "var_pct": var_otros,
            }
        )

    return rows


class Analizer(Stage):
    def __init__(self, municipio_id: str):
        self.municipio_id = municipio_id

    def execute(self, input_data: dict) -> dict:
        cve_mun = input_data["cve_mun"]
        municipio_id_str = str(self.municipio_id)

        try:
            region = get_region(municipio_id_str)
            region_municipios = get_same_region(municipio_id_str)
        except ValueError:
            region = ND
            region_municipios = []

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

        ctx = {}

        ctx["ec_municipio_nombre"] = input_data.get("municipio_nombre") or ND

        ctx["ec_region"] = region if region != ND else ND

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
            ctx["ec_anio_pasado_denue"] = ultima_act.year
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
        ctx["ec_sector_mayor_unidades"] = top3[0]["sector"]
        ctx["ec_porcentaje_sector_mayor_unidades"] = top3[0]["pct"]
        ctx["ec_sector_segundo_unidades"] = top3[1]["sector"]
        ctx["ec_porcentaje_sector_segundo_unidades"] = top3[1]["pct"]
        ctx["ec_sector_tercer_unidades"] = top3[2]["sector"]
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

        ctx["ec_anio_ce"] = anio_ce
        ctx["ec_anio_ce_anterior"] = anio_ce_anterior

        if vacb_total_actual and vacb_total_anterior:
            var_vacb = (
                (vacb_total_actual - vacb_total_anterior) / vacb_total_anterior * 100
            )
            ctx["ec_variacion_valor_agregado_censal"] = _pct(var_vacb)
            ctx["ec_variacion_vacb_total"] = _fmt(var_vacb)
        else:
            ctx["ec_variacion_valor_agregado_censal"] = ND
            ctx["ec_variacion_vacb_total"] = ND

        top3_vacb = vacb_actual[:3] if len(vacb_actual) >= 3 else vacb_actual
        ctx["ec_subsector_primer_lugar"] = (
            top3_vacb[0]["subsector"] if len(top3_vacb) > 0 else ND
        )
        ctx["ec_subsector_segundo_lugar"] = (
            top3_vacb[1]["subsector"] if len(top3_vacb) > 1 else ND
        )
        ctx["ec_subsector_tercer_lugar"] = (
            top3_vacb[2]["subsector"] if len(top3_vacb) > 2 else ND
        )

        if len(top3_vacb) >= 3 and vacb_total_actual:
            suma_top3 = sum(r["vacb"] for r in top3_vacb if r["vacb"])
            ctx["ec_porcentaje_aportacion_principales_subsectores"] = _pct(
                suma_top3 / vacb_total_actual * 100
            )
            ctx["ec_aportacion_principales_subsectores"] = _fmt(suma_top3, 2)
        else:
            ctx["ec_porcentaje_aportacion_principales_subsectores"] = ND
            ctx["ec_aportacion_principales_subsectores"] = ND

        anterior_by_codigo2 = {r["codigo"]: r["vacb"] for r in vacb_anterior}
        mayor_crecimiento = None
        mayor_tasa = None
        for r in vacb_actual:
            vact = r["vacb"]
            vant = anterior_by_codigo2.get(r["codigo"])
            if vact and vant:
                tasa = (vact - vant) / vant * 100
                if mayor_tasa is None or tasa > mayor_tasa:
                    mayor_tasa = tasa
                    mayor_crecimiento = r

        if mayor_crecimiento:
            sub_mc = mayor_crecimiento["subsector"]
            vact_mc = mayor_crecimiento["vacb"]
            vant_mc = anterior_by_codigo2.get(mayor_crecimiento["codigo"])
            ctx["ec_subsector_mayor_crecimiento"] = sub_mc
            ctx["ec_aportacion_anterior_subsector_mayor_crecimiento"] = (
                _fmt(vant_mc, 2) if vant_mc else ND
            )
            ctx["ec_aportacion_subsector_mayor_crecimiento"] = (
                _fmt(vact_mc, 2) if vact_mc else ND
            )
            ctx["ec_variacion_porcentual_aportacion_subsector_mayor_crecimiento"] = (
                _pct(mayor_tasa) if mayor_tasa is not None else ND
            )
        else:
            ctx["ec_subsector_mayor_crecimiento"] = ND
            ctx["ec_aportacion_anterior_subsector_mayor_crecimiento"] = ND
            ctx["ec_aportacion_subsector_mayor_crecimiento"] = ND
            ctx["ec_variacion_porcentual_aportacion_subsector_mayor_crecimiento"] = ND

        ctx["ec_tabla_vacb"] = _build_vacb_table(
            vacb_actual, vacb_anterior, vacb_total_actual
        )
        ctx["ec_vacb_total_anterior"] = (
            _fmt(vacb_total_anterior, 2) if vacb_total_anterior else ND
        )
        ctx["ec_vacb_total_actual"] = (
            _fmt(vacb_total_actual, 2) if vacb_total_actual else ND
        )

        ctx["ec_mes_corte_imss"] = ND
        ctx["ec_anio_corte_imss"] = ND
        ctx["ec_anio_anterior_corte_imss"] = ND
        ctx["ec_dos_anios_atras_corte_imss"] = ND
        ctx["ec_total_trabajadores_imss"] = ND
        ctx["ec_porcentaje_trabajadores_asegurados_jalisco"] = ND
        ctx["ec_porcentaje_variacion_asegurados"] = ND
        ctx["ec_grupo_ec_con_mas_empleos"] = ND
        ctx["ec_num_trabajadores_grupo_mayor"] = ND
        ctx["ec_porcentaje_trabajadores_grupo_mayor"] = ND
        ctx["ec_tabla_imss_grupos"] = []
        ctx["ec_posicion_municipio_region"] = ND
        ctx["ec_porcentaje_asegurados_region"] = ND
        ctx["ec_tabla_imss_region"] = []

        ctx["ec_anio_corte_sagarpa"] = ND
        ctx["ec_valor_produccion_agricola"] = ND
        ctx["ec_porcentaje_respecto_al_estado_agricola"] = ND
        ctx["ec_valor_produccion_ganado"] = ND
        ctx["ec_porcentaje_respecto_al_estado_ganado"] = ND
        ctx["ec_grafica_agricultura"] = MAPA_PLACEHOLDER
        ctx["ec_grafica_ganaderia"] = MAPA_PLACEHOLDER

        return ctx
