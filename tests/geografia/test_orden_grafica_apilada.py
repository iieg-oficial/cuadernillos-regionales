from pipelines.geografia.charts.treemap import _ordered_segments, _stacked_legend_order

SITUACION = {
    "Sin Disponibilidad": 60.19,
    "Sin clasificación": 21.31,
    "Con Disponibilidad": 18.5,
}
CONDICION = {"No explotado": 78.69, "Sin clasificación": 21.31}


def test_las_categorias_siguen_el_orden_del_mapa_de_colores():
    orden = [cat for cat, _ in _ordered_segments("acuiferos", SITUACION)]
    assert orden == ["Con Disponibilidad", "Sin Disponibilidad", "Sin clasificación"]


def test_la_categoria_residual_queda_al_final():
    orden = [cat for cat, _ in _ordered_segments("acuiferos", CONDICION)]
    assert orden[-1] == "Sin clasificación"


def test_las_categorias_en_cero_se_descartan():
    vals = {**CONDICION, "Sobreexplotado": 0.0}
    orden = [cat for cat, _ in _ordered_segments("acuiferos", vals)]
    assert "Sobreexplotado" not in orden


def test_sin_mapa_explicito_ordena_por_valor_descendente():
    vals = {"Veda": 10.0, "Reserva": 80.0, "Sin ordenamiento": 10.0}
    orden = [cat for cat, _ in _ordered_segments("cuencas", vals)]
    assert orden[0] == "Reserva"


def test_la_leyenda_sigue_el_orden_de_aparicion_de_arriba_hacia_abajo():
    row_data = [("Condición", CONDICION), ("Situación", SITUACION)]
    assert _stacked_legend_order("acuiferos", row_data) == [
        "Con Disponibilidad",
        "Sin Disponibilidad",
        "Sin clasificación",
        "No explotado",
    ]
