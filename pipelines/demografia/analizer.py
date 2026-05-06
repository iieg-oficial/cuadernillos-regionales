from core.pipelines.stage import Stage
from core.utils.municipalities import get_same_region

ND = "\\ND"
MAPA_PLACEHOLDER = (
    "\\includegraphics[width=\\textwidth]{templates/assets/mapa_placeholder.png}"
)
JALISCO_ID = 14
ANIO_CENSO = 2020
ANIO_INTERCENSAL = 2015
ANIO_CENSO_ANTERIOR = 2010


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


def _classify_grade(value: float, all_values: list[float]) -> str:
    sorted_vals = sorted(all_values)
    n = len(sorted_vals)
    rank = next((i for i, v in enumerate(sorted_vals) if v >= value), n - 1)
    pct = rank / n
    if pct < 0.2:
        return "Muy bajo"
    elif pct < 0.4:
        return "Bajo"
    elif pct < 0.6:
        return "Medio"
    elif pct < 0.8:
        return "Alto"
    return "Muy alto"


def _rank_desc(value: float, all_values: list[float]) -> int:
    sorted_desc = sorted(all_values, reverse=True)
    return next(
        (i + 1 for i, v in enumerate(sorted_desc) if v <= value), len(sorted_desc)
    )


class Analizer(Stage):
    def __init__(self, municipio_id: str):
        self.municipio_id = municipio_id

    def execute(self, input_data: dict) -> dict:
        cvegeo = 14000 + int(self.municipio_id)
        cve_mun = int(self.municipio_id)

        nombre = input_data["municipio_nombre"]
        totales = input_data["totales_poblacion"]
        localidades_2020 = input_data["localidades_2020"]
        localidades_2010 = input_data["localidades_2010"]
        iim_mun_2020 = input_data["iim_municipios_2020"]
        iim_mun_2010 = input_data["iim_municipios_2010"]
        iim_estados_2020 = input_data["iim_estados_2020"]
        marginacion_2020 = input_data["marginacion_jalisco_2020"]
        marginacion_2015 = input_data["marginacion_jalisco_2015"]
        marginacion_2010 = input_data["marginacion_jalisco_2010"]
        marginacion_localidades = input_data["marginacion_localidades"]
        marginacion_estatal_2020 = input_data["marginacion_estatal_2020"]

        ctx = {}

        ctx["de_municipio_nombre"] = nombre
        ctx["de_clave_entidad"] = "14"
        ctx["de_clave_municipio"] = f"14{cve_mun:03d}"
        ctx["de_anio_censo"] = ANIO_CENSO
        ctx["de_anio_encuesta_intercensal"] = ANIO_INTERCENSAL
        ctx["de_anio_censo_anterior"] = ANIO_CENSO_ANTERIOR

        t2020 = totales.get(ANIO_CENSO, {})
        t2015 = totales.get(ANIO_INTERCENSAL, {})
        t2010 = totales.get(ANIO_CENSO_ANTERIOR, {})

        total_2020 = t2020.get("total", 0) or 0
        total_2015 = t2015.get("total", 0) or 0
        total_2010 = t2010.get("total", 0) or 0

        ctx["de_poblacion_total_censo"] = _fmt_int(total_2020)

        if total_2020:
            h = t2020.get("hombres") or 0
            m = t2020.get("mujeres") or 0
            ctx["de_porcentaje_hombres"] = _pct(h / total_2020 * 100)
            ctx["de_porcentaje_mujeres"] = _pct(m / total_2020 * 100)
        else:
            ctx["de_porcentaje_hombres"] = ND
            ctx["de_porcentaje_mujeres"] = ND

        var_2015_2020 = total_2020 - total_2015
        ctx["de_variacion_poblacion_quinquenio_anterior"] = _fmt_int(var_2015_2020)
        ctx["de_variacion_porcentual_poblacion_quinquenio_anterior"] = (
            _pct(var_2015_2020 / total_2015 * 100) if total_2015 else ND
        )

        var_2010_2020 = total_2020 - total_2010
        ctx["de_variacion_poblacion_quinquenio"] = _fmt_int(var_2010_2020)
        ctx["de_variacion_porcentual_poblacion_quinquenio"] = (
            _pct(var_2010_2020 / total_2010 * 100) if total_2010 else ND
        )

        mujeres_2010 = t2010.get("mujeres") or 0
        mujeres_2015 = t2015.get("mujeres") or 0
        mujeres_2020 = t2020.get("mujeres") or 0
        hombres_2010 = t2010.get("hombres") or 0
        hombres_2015 = t2015.get("hombres") or 0
        hombres_2020 = t2020.get("hombres") or 0

        ctx["de_tabla_pob_mujeres_2010"] = (
            _fmt_int(mujeres_2010) if mujeres_2010 else ND
        )
        ctx["de_tabla_pob_mujeres_2015"] = (
            _fmt_int(mujeres_2015) if mujeres_2015 else ND
        )
        ctx["de_tabla_pob_mujeres_2020"] = (
            _fmt_int(mujeres_2020) if mujeres_2020 else ND
        )
        ctx["de_tabla_pob_hombres_2010"] = (
            _fmt_int(hombres_2010) if hombres_2010 else ND
        )
        ctx["de_tabla_pob_hombres_2015"] = (
            _fmt_int(hombres_2015) if hombres_2015 else ND
        )
        ctx["de_tabla_pob_hombres_2020"] = (
            _fmt_int(hombres_2020) if hombres_2020 else ND
        )
        ctx["de_tabla_pob_total_2010"] = _fmt_int(total_2010) if total_2010 else ND
        ctx["de_tabla_pob_total_2015"] = _fmt_int(total_2015) if total_2015 else ND
        ctx["de_tabla_pob_total_2020"] = _fmt_int(total_2020) if total_2020 else ND
        ctx["de_tabla_pob_var_pct_mujeres_2010_2015"] = (
            _pct((mujeres_2015 - mujeres_2010) / mujeres_2010 * 100)
            if (mujeres_2010 and mujeres_2015)
            else ND
        )
        ctx["de_tabla_pob_var_pct_mujeres_2015_2020"] = (
            _pct((mujeres_2020 - mujeres_2015) / mujeres_2015 * 100)
            if (mujeres_2015 and mujeres_2020)
            else ND
        )
        ctx["de_tabla_pob_var_pct_hombres_2010_2015"] = (
            _pct((hombres_2015 - hombres_2010) / hombres_2010 * 100)
            if (hombres_2010 and hombres_2015)
            else ND
        )
        ctx["de_tabla_pob_var_pct_hombres_2015_2020"] = (
            _pct((hombres_2020 - hombres_2015) / hombres_2015 * 100)
            if (hombres_2015 and hombres_2020)
            else ND
        )
        ctx["de_tabla_pob_var_pct_total_2010_2015"] = (
            _pct((total_2015 - total_2010) / total_2010 * 100)
            if (total_2010 and total_2015)
            else ND
        )
        ctx["de_tabla_pob_var_pct_total_2015_2020"] = (
            _pct((total_2020 - total_2015) / total_2015 * 100)
            if (total_2015 and total_2020)
            else ND
        )

        ctx["de_numero_localidades"] = len(localidades_2020)
        if localidades_2020:
            top = localidades_2020[0]
            ctx["de_loc_mas_poblada"] = top["localidad"]
            ctx["de_loc_mas_poblada_habitantes"] = _fmt_int(top["total"])
            ctx["de_porcentaje_habitantes_loc_mas_poblada"] = (
                _pct(top["total"] / total_2020 * 100) if total_2020 else ND
            )
        else:
            ctx["de_loc_mas_poblada"] = ND
            ctx["de_loc_mas_poblada_habitantes"] = ND
            ctx["de_porcentaje_habitantes_loc_mas_poblada"] = ND

        loc_2010_by_clave = {loc["clave"]: loc for loc in localidades_2010}
        ctx["de_localidades"] = [
            {
                "clave": str(loc["clave"]),
                "nombre": loc["localidad"],
                "total_2010": _fmt_int(loc_2010_by_clave[loc["clave"]]["total"])
                if loc["clave"] in loc_2010_by_clave
                else ND,
                "total_2020": _fmt_int(loc["total"]),
                "hombres_2020": _fmt_int(loc["hombres"]) if loc.get("hombres") else ND,
                "mujeres_2020": _fmt_int(loc["mujeres"]) if loc.get("mujeres") else ND,
                "pct_2020": _pct(loc["total"] / total_2020 * 100) if total_2020 else ND,
                "var_pct_2010_2020": _pct(
                    (loc["total"] - loc_2010_by_clave[loc["clave"]]["total"])
                    / loc_2010_by_clave[loc["clave"]]["total"]
                    * 100
                )
                if (
                    loc["clave"] in loc_2010_by_clave
                    and loc_2010_by_clave[loc["clave"]]["total"]
                )
                else ND,
            }
            for loc in localidades_2020[:5]
        ]

        jal_2020 = next(
            (e for e in iim_estados_2020 if e["entidad_id"] == JALISCO_ID), None
        )
        all_estado_vals = [
            e["iim_dp2"] for e in iim_estados_2020 if e["iim_dp2"] is not None
        ]

        if jal_2020 and jal_2020["iim_dp2"] is not None:
            ctx["de_grado_intensidad_migratoria_jal"] = _classify_grade(
                jal_2020["iim_dp2"], all_estado_vals
            )
            ctx["de_ranking_jal_migracion"] = _rank_desc(
                jal_2020["iim_dp2"], all_estado_vals
            )
            ctx["de_porcentaje_viviendas_remesas_jal"] = _pct(
                jal_2020.get("por_viv_remesas")
            )
            ctx["de_porcentaje_emigrantes_jal"] = _pct(
                jal_2020.get("por_viv_emigrantes")
            )
            ctx["de_porcentaje_migrantes_circulares_jal"] = _pct(
                jal_2020.get("por_viv_circ")
            )
            ctx["de_porcentaje_migrantes_retorno_jal"] = _pct(
                jal_2020.get("por_viv_reto")
            )
            ctx["de_jal_grado_migracion"] = jal_2020.get("grado_iim") or ND
            ctx["de_jal_lugar_migracion"] = (
                jal_2020.get("lugar_contexto_nacional") or ND
            )
        else:
            ctx["de_grado_intensidad_migratoria_jal"] = ND
            ctx["de_ranking_jal_migracion"] = ND
            ctx["de_porcentaje_viviendas_remesas_jal"] = ND
            ctx["de_porcentaje_emigrantes_jal"] = ND
            ctx["de_porcentaje_migrantes_circulares_jal"] = ND
            ctx["de_porcentaje_migrantes_retorno_jal"] = ND
            ctx["de_jal_grado_migracion"] = ND
            ctx["de_jal_lugar_migracion"] = ND

        jalisco_mun_2020 = [
            m for m in iim_mun_2020 if 14000 < m["municipio_id"] < 15000
        ]
        all_mun_vals_2020 = [
            m["iim_dp2"] for m in iim_mun_2020 if m["iim_dp2"] is not None
        ]
        jal_mun_vals_2020 = [
            m["iim_dp2"] for m in jalisco_mun_2020 if m["iim_dp2"] is not None
        ]

        mun_2020 = next(
            (m for m in jalisco_mun_2020 if m["municipio_id"] == cvegeo), None
        )
        if mun_2020 and mun_2020["iim_dp2"] is not None:
            ctx["de_grado_intensidad_migratoria_mun"] = _classify_grade(
                mun_2020["iim_dp2"], jal_mun_vals_2020
            )
            ctx["de_ranking_mun_migracion"] = _rank_desc(
                mun_2020["iim_dp2"], jal_mun_vals_2020
            )
            ctx["de_porcentaje_viviendas_remesas_mun"] = _pct(
                mun_2020.get("por_viv_remesas")
            )
            ctx["de_porcentaje_emigrantes_mun"] = _pct(
                mun_2020.get("por_viv_emigrantes")
            )
            ctx["de_porcentaje_migrantes_circulares_mun"] = _pct(
                mun_2020.get("por_viv_circ")
            )
            ctx["de_porcentaje_migrantes_retorno_mun"] = _pct(
                mun_2020.get("por_viv_reto")
            )
            ctx["de_grado_intensidad_migratoria"] = ctx[
                "de_grado_intensidad_migratoria_mun"
            ]
            ctx["de_ranking_migracion"] = ctx["de_ranking_mun_migracion"]
            ctx["de_ranking_nacional_mun_migracion"] = (
                mun_2020.get("lugar_contexto_nacional") or ND
            )
        else:
            ctx["de_grado_intensidad_migratoria_mun"] = ND
            ctx["de_ranking_mun_migracion"] = ND
            ctx["de_porcentaje_viviendas_remesas_mun"] = ND
            ctx["de_porcentaje_emigrantes_mun"] = ND
            ctx["de_porcentaje_migrantes_circulares_mun"] = ND
            ctx["de_porcentaje_migrantes_retorno_mun"] = ND
            ctx["de_grado_intensidad_migratoria"] = ND
            ctx["de_ranking_migracion"] = ND
            ctx["de_ranking_nacional_mun_migracion"] = ND

        jalisco_mun_2010 = [
            m for m in iim_mun_2010 if 14000 < m["municipio_id"] < 15000
        ]
        all_mun_vals_2010 = [
            m["iim_dp2"] for m in iim_mun_2010 if m["iim_dp2"] is not None
        ]
        jal_mun_vals_2010 = [
            m["iim_dp2"] for m in jalisco_mun_2010 if m["iim_dp2"] is not None
        ]
        mun_2010 = next(
            (m for m in jalisco_mun_2010 if m["municipio_id"] == cvegeo), None
        )

        if mun_2010 and mun_2010["iim_dp2"] is not None:
            ctx["de_grado_intensidad_migratoria_anterior_mun"] = _classify_grade(
                mun_2010["iim_dp2"], all_mun_vals_2010
            )
            ctx["de_ranking_anterior_mun_migracion"] = _rank_desc(
                mun_2010["iim_dp2"], jal_mun_vals_2010
            )
            ctx["de_ranking_nacional_mun_migracion_2010"] = (
                mun_2010.get("lugar_contexto_nacional") or ND
            )
            ctx["de_porcentaje_migrantes_circulares_anterior_mun"] = _pct(
                mun_2010.get("por_viv_circ")
            )
        else:
            ctx["de_grado_intensidad_migratoria_anterior_mun"] = ND
            ctx["de_ranking_anterior_mun_migracion"] = ND
            ctx["de_ranking_nacional_mun_migracion_2010"] = ND
            ctx["de_porcentaje_migrantes_circulares_anterior_mun"] = ND

        ctx["de_iim_mun_2010"] = (
            _fmt(mun_2010["iim_dp2"], 4)
            if (mun_2010 and mun_2010.get("iim_dp2") is not None)
            else ND
        )
        ctx["de_iim_mun_2020"] = (
            _fmt(mun_2020["iim_dp2"], 4)
            if (mun_2020 and mun_2020.get("iim_dp2") is not None)
            else ND
        )
        ctx["de_viv_totales_mun_2010"] = (
            _fmt_int(mun_2010["viv_totales"])
            if (mun_2010 and mun_2010.get("viv_totales"))
            else ND
        )
        ctx["de_viv_totales_mun_2020"] = (
            _fmt_int(mun_2020["viv_totales"])
            if (mun_2020 and mun_2020.get("viv_totales"))
            else ND
        )
        ctx["de_por_viv_remesas_mun_2010"] = (
            _pct(mun_2010.get("por_viv_remesas")) if mun_2010 else ND
        )
        ctx["de_por_viv_remesas_mun_2020"] = (
            _pct(mun_2020.get("por_viv_remesas")) if mun_2020 else ND
        )
        ctx["de_por_viv_emigrantes_mun_2010"] = (
            _pct(mun_2010.get("por_viv_emigrantes")) if mun_2010 else ND
        )
        ctx["de_por_viv_emigrantes_mun_2020"] = (
            _pct(mun_2020.get("por_viv_emigrantes")) if mun_2020 else ND
        )
        ctx["de_por_viv_retorno_mun_2010"] = (
            _pct(mun_2010.get("por_viv_reto")) if mun_2010 else ND
        )
        ctx["de_por_viv_retorno_mun_2020"] = (
            _pct(mun_2020.get("por_viv_reto")) if mun_2020 else ND
        )

        ctx["de_mapa_grado_intensidad_migratoria"] = MAPA_PLACEHOLDER

        mun_marg_2020 = next(
            (m for m in marginacion_2020 if m["municipio_id"] == cvegeo), None
        )
        mun_marg_2015 = next(
            (m for m in marginacion_2015 if m["municipio_id"] == cvegeo), None
        )
        mun_marg_2010 = next(
            (m for m in marginacion_2010 if m["municipio_id"] == cvegeo), None
        )

        def _marg_ranking(municipio_id, marg_list):
            return next(
                (
                    i + 1
                    for i, m in enumerate(marg_list)
                    if m["municipio_id"] == municipio_id
                ),
                ND,
            )

        if mun_marg_2020:
            ctx["de_grado_marginacion_municipio"] = (
                mun_marg_2020.get("grado_marginacion") or ND
            )
            ctx["de_ranking_marginacion_municipio"] = _marg_ranking(
                cvegeo, marginacion_2020
            )
            ctx["de_grado_marginacion"] = ctx["de_grado_marginacion_municipio"]
            ctx["de_ranking_marginacion"] = ctx["de_ranking_marginacion_municipio"]
            ctx["de_marg_indice_2020"] = _fmt(
                mun_marg_2020.get("indice_marginacion"), 4
            )
            ctx["de_marg_grado_2020"] = mun_marg_2020.get("grado_marginacion") or ND
            ctx["de_marg_analfabeta_2020"] = _pct(
                mun_marg_2020.get("porc_pob15_analfabeta")
            )
            ctx["de_marg_sin_educ_bas_2020"] = _pct(
                mun_marg_2020.get("pob15_sin_educ_bas")
            )
            ctx["de_marg_sin_drenaje_2020"] = _pct(
                mun_marg_2020.get("porc_viv_sin_drenaje_ni_excusado")
            )
            ctx["de_marg_sin_energia_2020"] = _pct(
                mun_marg_2020.get("porc_viv_sin_energia")
            )
            ctx["de_marg_sin_agua_2020"] = _pct(
                mun_marg_2020.get("porc_viv_sin_agua_entubada")
            )
            ctx["de_marg_piso_tierra_2020"] = _pct(
                mun_marg_2020.get("porc_viv_piso_tierra")
            )
            ctx["de_marg_hacinamiento_2020"] = _fmt(
                mun_marg_2020.get("prom_ocup_por_cuarto"), 2
            )
            ctx["de_marg_loc_menos5000_2020"] = _pct(
                mun_marg_2020.get("porc_pob_loc_menos5000_hab")
            )
            ctx["de_marg_hasta2salmin_2020"] = _pct(
                mun_marg_2020.get("pob_ocup_hasta_2_sal_min")
            )
            ctx["de_marg_sin_refrigerador_2020"] = _pct(
                mun_marg_2020.get("porc_viv_sin_refrigerador")
            )
            ctx["de_marg_pos_entidad_2020"] = ctx["de_ranking_marginacion_municipio"]
            ctx["de_marg_pos_nacional_2020"] = (
                mun_marg_2020.get("lugar_contexto_nacional") or ND
            )
        else:
            ctx["de_grado_marginacion_municipio"] = ND
            ctx["de_ranking_marginacion_municipio"] = ND
            ctx["de_grado_marginacion"] = ND
            ctx["de_ranking_marginacion"] = ND
            ctx["de_marg_indice_2020"] = ND
            ctx["de_marg_grado_2020"] = ND
            ctx["de_marg_analfabeta_2020"] = ND
            ctx["de_marg_sin_educ_bas_2020"] = ND
            ctx["de_marg_sin_drenaje_2020"] = ND
            ctx["de_marg_sin_energia_2020"] = ND
            ctx["de_marg_sin_agua_2020"] = ND
            ctx["de_marg_piso_tierra_2020"] = ND
            ctx["de_marg_hacinamiento_2020"] = ND
            ctx["de_marg_loc_menos5000_2020"] = ND
            ctx["de_marg_hasta2salmin_2020"] = ND
            ctx["de_marg_sin_refrigerador_2020"] = ND
            ctx["de_marg_pos_entidad_2020"] = ND
            ctx["de_marg_pos_nacional_2020"] = ND

        if mun_marg_2015:
            ctx["de_marg_indice_2015"] = _fmt(
                mun_marg_2015.get("indice_marginacion"), 4
            )
            ctx["de_marg_grado_2015"] = mun_marg_2015.get("grado_marginacion") or ND
            ctx["de_marg_analfabeta_2015"] = _pct(
                mun_marg_2015.get("porc_pob15_analfabeta")
            )
            ctx["de_marg_sin_educ_bas_2015"] = _pct(
                mun_marg_2015.get("pob15_sin_educ_bas")
            )
            ctx["de_marg_sin_drenaje_2015"] = _pct(
                mun_marg_2015.get("porc_viv_sin_drenaje_ni_excusado")
            )
            ctx["de_marg_sin_energia_2015"] = _pct(
                mun_marg_2015.get("porc_viv_sin_energia")
            )
            ctx["de_marg_sin_agua_2015"] = _pct(
                mun_marg_2015.get("porc_viv_sin_agua_entubada")
            )
            ctx["de_marg_piso_tierra_2015"] = _pct(
                mun_marg_2015.get("porc_viv_piso_tierra")
            )
            ctx["de_marg_hacinamiento_2015"] = _fmt(
                mun_marg_2015.get("prom_ocup_por_cuarto"), 2
            )
            ctx["de_marg_loc_menos5000_2015"] = _pct(
                mun_marg_2015.get("porc_pob_loc_menos5000_hab")
            )
            ctx["de_marg_hasta2salmin_2015"] = _pct(
                mun_marg_2015.get("pob_ocup_hasta_2_sal_min")
            )
            ctx["de_marg_pos_entidad_2015"] = _marg_ranking(cvegeo, marginacion_2015)
            ctx["de_marg_pos_nacional_2015"] = (
                mun_marg_2015.get("lugar_contexto_nacional") or ND
            )
            ctx["de_grado_marginacion_intercensal_mun"] = (
                mun_marg_2015.get("grado_marginacion") or ND
            )
            ctx["de_ranking_marginacion_intercensal_mun"] = ctx[
                "de_marg_pos_entidad_2015"
            ]
        else:
            ctx["de_marg_indice_2015"] = ND
            ctx["de_marg_grado_2015"] = ND
            ctx["de_marg_analfabeta_2015"] = ND
            ctx["de_marg_sin_educ_bas_2015"] = ND
            ctx["de_marg_sin_drenaje_2015"] = ND
            ctx["de_marg_sin_energia_2015"] = ND
            ctx["de_marg_sin_agua_2015"] = ND
            ctx["de_marg_piso_tierra_2015"] = ND
            ctx["de_marg_hacinamiento_2015"] = ND
            ctx["de_marg_loc_menos5000_2015"] = ND
            ctx["de_marg_hasta2salmin_2015"] = ND
            ctx["de_marg_pos_entidad_2015"] = ND
            ctx["de_marg_pos_nacional_2015"] = ND
            ctx["de_grado_marginacion_intercensal_mun"] = ND
            ctx["de_ranking_marginacion_intercensal_mun"] = ND

        if mun_marg_2010:
            ctx["de_marg_indice_2010"] = _fmt(
                mun_marg_2010.get("indice_marginacion"), 4
            )
            ctx["de_marg_grado_2010"] = mun_marg_2010.get("grado_marginacion") or ND
            ctx["de_marg_analfabeta_2010"] = _pct(
                mun_marg_2010.get("porc_pob15_analfabeta")
            )
            ctx["de_marg_sin_educ_bas_2010"] = _pct(
                mun_marg_2010.get("pob15_sin_educ_bas")
            )
            ctx["de_marg_sin_drenaje_2010"] = _pct(
                mun_marg_2010.get("porc_viv_sin_drenaje_ni_excusado")
            )
            ctx["de_marg_sin_energia_2010"] = _pct(
                mun_marg_2010.get("porc_viv_sin_energia")
            )
            ctx["de_marg_sin_agua_2010"] = _pct(
                mun_marg_2010.get("porc_viv_sin_agua_entubada")
            )
            ctx["de_marg_piso_tierra_2010"] = _pct(
                mun_marg_2010.get("porc_viv_piso_tierra")
            )
            ctx["de_marg_hacinamiento_2010"] = _fmt(
                mun_marg_2010.get("prom_ocup_por_cuarto"), 2
            )
            ctx["de_marg_loc_menos5000_2010"] = _pct(
                mun_marg_2010.get("porc_pob_loc_menos5000_hab")
            )
            ctx["de_marg_hasta2salmin_2010"] = _pct(
                mun_marg_2010.get("pob_ocup_hasta_2_sal_min")
            )
            ctx["de_marg_pos_entidad_2010"] = _marg_ranking(cvegeo, marginacion_2010)
            ctx["de_marg_pos_nacional_2010"] = (
                mun_marg_2010.get("lugar_contexto_nacional") or ND
            )
            ctx["de_grado_marginacion_anterior"] = (
                mun_marg_2010.get("grado_marginacion") or ND
            )
            ctx["de_ranking_marginacion_censo_anterior"] = ctx[
                "de_marg_pos_entidad_2010"
            ]
        else:
            ctx["de_marg_indice_2010"] = ND
            ctx["de_marg_grado_2010"] = ND
            ctx["de_marg_analfabeta_2010"] = ND
            ctx["de_marg_sin_educ_bas_2010"] = ND
            ctx["de_marg_sin_drenaje_2010"] = ND
            ctx["de_marg_sin_energia_2010"] = ND
            ctx["de_marg_sin_agua_2010"] = ND
            ctx["de_marg_piso_tierra_2010"] = ND
            ctx["de_marg_hacinamiento_2010"] = ND
            ctx["de_marg_loc_menos5000_2010"] = ND
            ctx["de_marg_hasta2salmin_2010"] = ND
            ctx["de_marg_pos_entidad_2010"] = ND
            ctx["de_marg_pos_nacional_2010"] = ND
            ctx["de_grado_marginacion_anterior"] = ND
            ctx["de_ranking_marginacion_censo_anterior"] = ND

        if marginacion_estatal_2020:
            ctx["de_grado_marginacion_jalisco"] = (
                marginacion_estatal_2020.get("grado_marginacion") or ND
            )
            ctx["de_jal_marg_grado"] = (
                marginacion_estatal_2020.get("grado_marginacion") or ND
            )
            ctx["de_jal_poblacion_2020"] = (
                _fmt_int(marginacion_estatal_2020["pob_total"])
                if marginacion_estatal_2020.get("pob_total")
                else ND
            )
            ctx["de_jal_marg_lugar_nacional"] = (
                marginacion_estatal_2020.get("lugar_contexto_nacional") or ND
            )
            ctx["de_jal_marg_analfabeta"] = _pct(
                marginacion_estatal_2020.get("porc_pob15_analfabeta")
            )
            ctx["de_jal_marg_sin_educ_bas"] = _pct(
                marginacion_estatal_2020.get("pob15_sin_educ_bas")
            )
            ctx["de_jal_marg_sin_drenaje"] = _pct(
                marginacion_estatal_2020.get("porc_viv_sin_drenaje_ni_excusado")
            )
            ctx["de_jal_marg_sin_energia"] = _pct(
                marginacion_estatal_2020.get("porc_viv_sin_energia")
            )
            ctx["de_jal_marg_sin_agua"] = _pct(
                marginacion_estatal_2020.get("porc_viv_sin_agua_entubada")
            )
            ctx["de_jal_marg_piso_tierra"] = _pct(
                marginacion_estatal_2020.get("porc_viv_piso_tierra")
            )
            ctx["de_jal_marg_hacinamiento"] = _pct(
                marginacion_estatal_2020.get("porc_viv_con_hacinamiento")
            )
            ctx["de_jal_marg_sin_refrigerador"] = _pct(
                marginacion_estatal_2020.get("porc_viv_sin_refrigerador")
            )
        else:
            ctx["de_grado_marginacion_jalisco"] = ND
            ctx["de_jal_marg_grado"] = ND
            ctx["de_jal_poblacion_2020"] = ND
            ctx["de_jal_marg_lugar_nacional"] = ND
            ctx["de_jal_marg_analfabeta"] = ND
            ctx["de_jal_marg_sin_educ_bas"] = ND
            ctx["de_jal_marg_sin_drenaje"] = ND
            ctx["de_jal_marg_sin_energia"] = ND
            ctx["de_jal_marg_sin_agua"] = ND
            ctx["de_jal_marg_piso_tierra"] = ND
            ctx["de_jal_marg_hacinamiento"] = ND
            ctx["de_jal_marg_sin_refrigerador"] = ND
        ctx["de_mapa_indice_marginacion_municipio"] = MAPA_PLACEHOLDER

        DASH = "{-}"
        marg_by_nombre = {loc["localidad"]: loc for loc in marginacion_localidades}

        def _loc_val(marg, key, fn):
            if marg is None:
                return DASH
            return fn(marg.get(key))

        top5_locs = localidades_2020[:5]
        hay_datos_faltantes = False
        locs_ctx = []
        for loc in top5_locs:
            marg = marg_by_nombre.get(loc["localidad"])
            sin_datos = marg is None
            if sin_datos:
                hay_datos_faltantes = True
            cvegeo = marg["cvegeo"] if marg else str(loc["clave"])
            locs_ctx.append(
                {
                    "clave": cvegeo,
                    "nombre": loc["localidad"],
                    "grado": DASH
                    if sin_datos
                    else (marg.get("grado_marginacion") or ND),
                    "analfabeta": _loc_val(marg, "porc_pob15_analfabeta", _pct),
                    "sin_educ_bas": _loc_val(marg, "porc_pob15_sin_educ_basica", _pct),
                    "sin_drenaje": _loc_val(
                        marg, "porc_viv_sin_drenaje_ni_excusado", _pct
                    ),
                    "sin_energia": _loc_val(marg, "porc_viv_sin_energia", _pct),
                    "sin_agua": _loc_val(marg, "porc_viv_sin_agua_entubada", _pct),
                    "piso_tierra": _loc_val(marg, "porc_viv_piso_tierra", _pct),
                    "hacinamiento": _loc_val(
                        marg, "prom_ocup_por_cuarto", lambda v: _fmt(v, 2)
                    ),
                    "sin_refrigerador": _loc_val(
                        marg, "porc_viv_sin_refrigerador", _pct
                    ),
                }
            )
        ctx["de_localidades_marginacion"] = locs_ctx
        ctx["de_localidades_hay_datos_faltantes"] = hay_datos_faltantes

        pobreza_2020 = input_data.get("pobreza_2020") or {}
        pobreza_2015 = input_data.get("pobreza_2015") or {}
        pobreza_jalisco_2020 = input_data.get("pobreza_jalisco_2020") or []
        pobreza_por_entidad_2020 = input_data.get("pobreza_por_entidad_2020") or []

        def _p(data, key, fn=_pct):
            return fn(data.get(key))

        ent_pob_rank = {
            r["cve_ent"]: i + 1
            for i, r in enumerate(
                sorted(
                    [
                        r
                        for r in pobreza_por_entidad_2020
                        if r.get("pobreza_porcentaje") is not None
                    ],
                    key=lambda r: r["pobreza_porcentaje"],
                )
            )
        }
        ent_pob_ext_rank = {
            r["cve_ent"]: i + 1
            for i, r in enumerate(
                sorted(
                    [
                        r
                        for r in pobreza_por_entidad_2020
                        if r.get("pobreza_ext_porcentaje") is not None
                    ],
                    key=lambda r: r["pobreza_ext_porcentaje"],
                )
            )
        }
        jal_ent = next(
            (r for r in pobreza_por_entidad_2020 if r["cve_ent"] == "14"), None
        )
        ctx["de_pobreza_jal_pct"] = (
            _pct(jal_ent["pobreza_porcentaje"]) if jal_ent else ND
        )
        ctx["de_pobreza_jal_ext_pct"] = (
            _pct(jal_ent["pobreza_ext_porcentaje"]) if jal_ent else ND
        )
        ctx["de_ranking_pobreza_jal"] = ent_pob_rank.get("14", ND)
        ctx["de_ranking_pobreza_ext_jal"] = ent_pob_ext_rank.get("14", ND)

        pob_by_cve = {r["cve_mun"]: r for r in pobreza_jalisco_2020}
        pob_rank = {
            r["cve_mun"]: i + 1
            for i, r in enumerate(
                sorted(
                    [
                        r
                        for r in pobreza_jalisco_2020
                        if r.get("pobreza_porcentaje") is not None
                    ],
                    key=lambda r: r["pobreza_porcentaje"],
                    reverse=True,
                )
            )
        }
        pob_ext_rank = {
            r["cve_mun"]: i + 1
            for i, r in enumerate(
                sorted(
                    [
                        r
                        for r in pobreza_jalisco_2020
                        if r.get("pobreza_ext_porcentaje") is not None
                    ],
                    key=lambda r: r["pobreza_ext_porcentaje"],
                    reverse=True,
                )
            )
        }

        iim_jal_rank = {
            m["municipio_id"]: i + 1
            for i, m in enumerate(
                sorted(
                    [m for m in jalisco_mun_2020 if m.get("iim_dp2") is not None],
                    key=lambda m: m["iim_dp2"],
                )
            )
        }

        region_ids = {int(m["id"]) for m in get_same_region(str(cve_mun))}
        marg_by_mun = {m["municipio_id"]: m for m in marginacion_2020}
        iim_by_mun = {m["municipio_id"]: m for m in jalisco_mun_2020}
        ctx["de_region_municipios"] = [
            {
                "clave": f"14{int(rid):03d}",
                "nombre": next(
                    m["municipio"]
                    for m in get_same_region(str(cve_mun))
                    if int(m["id"]) == rid
                ),
                "poblacion": _fmt_int(marg_by_mun[14000 + rid]["pob_total"])
                if (14000 + rid) in marg_by_mun
                and marg_by_mun[14000 + rid].get("pob_total")
                else ND,
                "grado_marginacion": marg_by_mun.get(14000 + rid, {}).get(
                    "grado_marginacion"
                )
                or ND,
                "lugar_marginacion": _marg_ranking(14000 + rid, marginacion_2020)
                if (14000 + rid) in marg_by_mun
                else ND,
                "grado_migracion": iim_by_mun.get(14000 + rid, {}).get("grado_iim")
                or ND,
                "lugar_migracion": iim_jal_rank.get(14000 + rid, ND),
                "pobreza_pct": _pct(
                    pob_by_cve.get(f"14{int(rid):03d}", {}).get("pobreza_porcentaje")
                ),
                "pobreza_lugar": pob_rank.get(f"14{int(rid):03d}", ND),
                "pobreza_ext_pct": _pct(
                    pob_by_cve.get(f"14{int(rid):03d}", {}).get(
                        "pobreza_ext_porcentaje"
                    )
                ),
                "pobreza_ext_lugar": pob_ext_rank.get(f"14{int(rid):03d}", ND),
            }
            for rid in sorted(region_ids)
            if rid != cve_mun
        ]

        ctx["de_porcentaje_pobreza"] = _p(pobreza_2020, "pobreza_porcentaje")
        ctx["de_poblacion_pobreza"] = _p(pobreza_2020, "pobreza_personas", _fmt_int)
        ctx["de_porcentaje_vulnerabilidad_carencias"] = _p(
            pobreza_2020, "vul_carencia_porcentaje"
        )
        ctx["de_poblacion_vulnerabilidad_carencias"] = _p(
            pobreza_2020, "vul_carencia_personas", _fmt_int
        )
        ctx["de_porcentaje_vulnerabilidad_ingresos"] = _p(
            pobreza_2020, "vul_ingreso_porcentaje"
        )
        ctx["de_porcentaje_no_pobre_no_vulnerable"] = _p(
            pobreza_2020, "no_pobre_porcentaje"
        )
        ctx["de_porcentaje_pobreza_extrema"] = _p(
            pobreza_2020, "pobreza_ext_porcentaje"
        )
        ctx["de_porcentaje_pobreza_extrema_intercensal"] = _p(
            pobreza_2015, "pobreza_ext_porcentaje"
        )
        ctx["de_porcentaje_pobreza_moderada"] = _p(
            pobreza_2020, "pobreza_mod_porcentaje"
        )
        ctx["de_poblacion_pobreza_moderada"] = _p(
            pobreza_2020, "pobreza_mod_personas", _fmt_int
        )
        ctx["de_porcentaje_pobreza_moderada_intercensal"] = _p(
            pobreza_2015, "pobreza_mod_porcentaje"
        )
        ctx["de_poblacion_pobreza_moderada_intercensal"] = _p(
            pobreza_2015, "pobreza_mod_personas", _fmt_int
        )

        ctx["de_pobreza_pct_2015"] = _p(pobreza_2015, "pobreza_porcentaje")
        ctx["de_pobreza_pct_2020"] = _p(pobreza_2020, "pobreza_porcentaje")
        ctx["de_pobreza_prs_2015"] = _p(pobreza_2015, "pobreza_personas", _fmt_int)
        ctx["de_pobreza_prs_2020"] = _p(pobreza_2020, "pobreza_personas", _fmt_int)
        ctx["de_pobreza_prom_2015"] = _p(pobreza_2015, "pobreza_promedio", _fmt)
        ctx["de_pobreza_prom_2020"] = _p(pobreza_2020, "pobreza_promedio", _fmt)

        ctx["de_pobreza_mod_pct_2015"] = _p(pobreza_2015, "pobreza_mod_porcentaje")
        ctx["de_pobreza_mod_pct_2020"] = _p(pobreza_2020, "pobreza_mod_porcentaje")
        ctx["de_pobreza_mod_prs_2015"] = _p(
            pobreza_2015, "pobreza_mod_personas", _fmt_int
        )
        ctx["de_pobreza_mod_prs_2020"] = _p(
            pobreza_2020, "pobreza_mod_personas", _fmt_int
        )
        ctx["de_pobreza_mod_prom_2015"] = _p(pobreza_2015, "pobreza_mod_promedio", _fmt)
        ctx["de_pobreza_mod_prom_2020"] = _p(pobreza_2020, "pobreza_mod_promedio", _fmt)

        ctx["de_pobreza_ext_pct_2015"] = _p(pobreza_2015, "pobreza_ext_porcentaje")
        ctx["de_pobreza_ext_pct_2020"] = _p(pobreza_2020, "pobreza_ext_porcentaje")
        ctx["de_pobreza_ext_prs_2015"] = _p(
            pobreza_2015, "pobreza_ext_personas", _fmt_int
        )
        ctx["de_pobreza_ext_prs_2020"] = _p(
            pobreza_2020, "pobreza_ext_personas", _fmt_int
        )
        ctx["de_pobreza_ext_prom_2015"] = _p(pobreza_2015, "pobreza_ext_promedio", _fmt)
        ctx["de_pobreza_ext_prom_2020"] = _p(pobreza_2020, "pobreza_ext_promedio", _fmt)

        ctx["de_vul_carencia_pct_2015"] = _p(pobreza_2015, "vul_carencia_porcentaje")
        ctx["de_vul_carencia_pct_2020"] = _p(pobreza_2020, "vul_carencia_porcentaje")
        ctx["de_vul_carencia_prs_2015"] = _p(
            pobreza_2015, "vul_carencia_personas", _fmt_int
        )
        ctx["de_vul_carencia_prs_2020"] = _p(
            pobreza_2020, "vul_carencia_personas", _fmt_int
        )
        ctx["de_vul_carencia_prom_2015"] = _p(
            pobreza_2015, "vul_carencia_promedio", _fmt
        )
        ctx["de_vul_carencia_prom_2020"] = _p(
            pobreza_2020, "vul_carencia_promedio", _fmt
        )

        ctx["de_vul_ingreso_pct_2015"] = _p(pobreza_2015, "vul_ingreso_porcentaje")
        ctx["de_vul_ingreso_pct_2020"] = _p(pobreza_2020, "vul_ingreso_porcentaje")
        ctx["de_vul_ingreso_prs_2015"] = _p(
            pobreza_2015, "vul_ingreso_personas", _fmt_int
        )
        ctx["de_vul_ingreso_prs_2020"] = _p(
            pobreza_2020, "vul_ingreso_personas", _fmt_int
        )

        ctx["de_no_pobre_pct_2015"] = _p(pobreza_2015, "no_pobre_porcentaje")
        ctx["de_no_pobre_pct_2020"] = _p(pobreza_2020, "no_pobre_porcentaje")
        ctx["de_no_pobre_prs_2015"] = _p(pobreza_2015, "no_pobre_personas", _fmt_int)
        ctx["de_no_pobre_prs_2020"] = _p(pobreza_2020, "no_pobre_personas", _fmt_int)

        ctx["de_al_1_car_pct_2015"] = _p(pobreza_2015, "al_1_car_porcentaje")
        ctx["de_al_1_car_pct_2020"] = _p(pobreza_2020, "al_1_car_porcentaje")
        ctx["de_al_1_car_prs_2015"] = _p(pobreza_2015, "al_1_car_personas", _fmt_int)
        ctx["de_al_1_car_prs_2020"] = _p(pobreza_2020, "al_1_car_personas", _fmt_int)
        ctx["de_al_1_car_prom_2015"] = _p(pobreza_2015, "al_1_car_promedio", _fmt)
        ctx["de_al_1_car_prom_2020"] = _p(pobreza_2020, "al_1_car_promedio", _fmt)

        ctx["de_tres_mas_car_pct_2015"] = _p(pobreza_2015, "tres_mas_car_porcentaje")
        ctx["de_tres_mas_car_pct_2020"] = _p(pobreza_2020, "tres_mas_car_porcentaje")
        ctx["de_tres_mas_car_prs_2015"] = _p(
            pobreza_2015, "tres_mas_car_personas", _fmt_int
        )
        ctx["de_tres_mas_car_prs_2020"] = _p(
            pobreza_2020, "tres_mas_car_personas", _fmt_int
        )
        ctx["de_tres_mas_car_prom_2015"] = _p(
            pobreza_2015, "tres_mas_car_promedio", _fmt
        )
        ctx["de_tres_mas_car_prom_2020"] = _p(
            pobreza_2020, "tres_mas_car_promedio", _fmt
        )

        ctx["de_rez_edu_pct_2015"] = _p(pobreza_2015, "rez_edu_porcentaje")
        ctx["de_rez_edu_pct_2020"] = _p(pobreza_2020, "rez_edu_porcentaje")
        ctx["de_rez_edu_prs_2015"] = _p(pobreza_2015, "rez_edu_personas", _fmt_int)
        ctx["de_rez_edu_prs_2020"] = _p(pobreza_2020, "rez_edu_personas", _fmt_int)
        ctx["de_rez_edu_prom_2015"] = _p(pobreza_2015, "rez_edu_promedio", _fmt)
        ctx["de_rez_edu_prom_2020"] = _p(pobreza_2020, "rez_edu_promedio", _fmt)

        ctx["de_car_salud_pct_2015"] = _p(pobreza_2015, "car_salud_porcentaje")
        ctx["de_car_salud_pct_2020"] = _p(pobreza_2020, "car_salud_porcentaje")
        ctx["de_car_salud_prs_2015"] = _p(pobreza_2015, "car_salud_personas", _fmt_int)
        ctx["de_car_salud_prs_2020"] = _p(pobreza_2020, "car_salud_personas", _fmt_int)
        ctx["de_car_salud_prom_2015"] = _p(pobreza_2015, "car_salud_promedio", _fmt)
        ctx["de_car_salud_prom_2020"] = _p(pobreza_2020, "car_salud_promedio", _fmt)

        ctx["de_car_seg_soc_pct_2015"] = _p(pobreza_2015, "car_seg_soc_porcentaje")
        ctx["de_car_seg_soc_pct_2020"] = _p(pobreza_2020, "car_seg_soc_porcentaje")
        ctx["de_car_seg_soc_prs_2015"] = _p(
            pobreza_2015, "car_seg_soc_personas", _fmt_int
        )
        ctx["de_car_seg_soc_prs_2020"] = _p(
            pobreza_2020, "car_seg_soc_personas", _fmt_int
        )
        ctx["de_car_seg_soc_prom_2015"] = _p(pobreza_2015, "car_seg_soc_promedio", _fmt)
        ctx["de_car_seg_soc_prom_2020"] = _p(pobreza_2020, "car_seg_soc_promedio", _fmt)

        ctx["de_car_viv_pct_2015"] = _p(pobreza_2015, "car_viv_porcentaje")
        ctx["de_car_viv_pct_2020"] = _p(pobreza_2020, "car_viv_porcentaje")
        ctx["de_car_viv_prs_2015"] = _p(pobreza_2015, "car_viv_personas", _fmt_int)
        ctx["de_car_viv_prs_2020"] = _p(pobreza_2020, "car_viv_personas", _fmt_int)
        ctx["de_car_viv_prom_2015"] = _p(pobreza_2015, "car_viv_promedio", _fmt)
        ctx["de_car_viv_prom_2020"] = _p(pobreza_2020, "car_viv_promedio", _fmt)

        ctx["de_car_sbv_pct_2015"] = _p(pobreza_2015, "car_sbv_porcentaje")
        ctx["de_car_sbv_pct_2020"] = _p(pobreza_2020, "car_sbv_porcentaje")
        ctx["de_car_sbv_prs_2015"] = _p(pobreza_2015, "car_sbv_personas", _fmt_int)
        ctx["de_car_sbv_prs_2020"] = _p(pobreza_2020, "car_sbv_personas", _fmt_int)
        ctx["de_car_sbv_prom_2015"] = _p(pobreza_2015, "car_sbv_promedio", _fmt)
        ctx["de_car_sbv_prom_2020"] = _p(pobreza_2020, "car_sbv_promedio", _fmt)

        ctx["de_car_ali_pct_2015"] = _p(pobreza_2015, "car_ali_porcentaje")
        ctx["de_car_ali_pct_2020"] = _p(pobreza_2020, "car_ali_porcentaje")
        ctx["de_car_ali_prs_2015"] = _p(pobreza_2015, "car_ali_personas", _fmt_int)
        ctx["de_car_ali_prs_2020"] = _p(pobreza_2020, "car_ali_personas", _fmt_int)
        ctx["de_car_ali_prom_2015"] = _p(pobreza_2015, "car_ali_promedio", _fmt)
        ctx["de_car_ali_prom_2020"] = _p(pobreza_2020, "car_ali_promedio", _fmt)

        ctx["de_lpei_pct_2015"] = _p(pobreza_2015, "lpei_porcentaje")
        ctx["de_lpei_pct_2020"] = _p(pobreza_2020, "lpei_porcentaje")
        ctx["de_lpei_prs_2015"] = _p(pobreza_2015, "lpei_personas", _fmt_int)
        ctx["de_lpei_prs_2020"] = _p(pobreza_2020, "lpei_personas", _fmt_int)
        ctx["de_lpei_prom_2015"] = _p(pobreza_2015, "lpei_promedio", _fmt)
        ctx["de_lpei_prom_2020"] = _p(pobreza_2020, "lpei_promedio", _fmt)

        ctx["de_lpi_pct_2015"] = _p(pobreza_2015, "lpi_porcentaje")
        ctx["de_lpi_pct_2020"] = _p(pobreza_2020, "lpi_porcentaje")
        ctx["de_lpi_prs_2015"] = _p(pobreza_2015, "lpi_personas", _fmt_int)
        ctx["de_lpi_prs_2020"] = _p(pobreza_2020, "lpi_personas", _fmt_int)
        ctx["de_lpi_prom_2015"] = _p(pobreza_2015, "lpi_promedio", _fmt)
        ctx["de_lpi_prom_2020"] = _p(pobreza_2020, "lpi_promedio", _fmt)

        ctx["de_mapa_porcentaje_pobreza_multidimensional"] = MAPA_PLACEHOLDER

        total_estatal = input_data.get("total_estatal_2020")
        ctx["de_porcentaje_poblacion"] = (
            _pct(total_2020 / total_estatal * 100)
            if (total_2020 and total_estatal)
            else ND
        )
        ctx["de_ranking_pobreza_multidimensional"] = pob_rank.get(
            f"14{cve_mun:03d}", ND
        )
        ctx["de_ranking_pobreza_extrema"] = pob_ext_rank.get(f"14{cve_mun:03d}", ND)

        return ctx
