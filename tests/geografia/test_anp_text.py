from pipelines.geografia.helpers.context import build_anp_text

ZAPOPAN = {
    "anp_nombre": "Zapopan",
    "anp_num_anp": "8",
    "anp_superficie_anp": "27\\,092.24",
    "anp_pct_anp": "26.63",
    "anp_pct_humedales": "0.35",
}


def test_no_menciona_superficie_ni_porcentaje_de_las_anp():
    texto = build_anp_text(ZAPOPAN)
    assert "hectáreas" not in texto
    assert "26.63" not in texto
    assert "27\\,092.24" not in texto


def test_cuenta_las_anp_y_luego_los_humedales():
    texto = build_anp_text(ZAPOPAN)
    assert texto.endswith(
        "el municipio de Zapopan registra 8 áreas naturales protegidas. "
        "Asimismo, los humedales abarcan 0.35 \\% del territorio municipal"
    )


def test_una_sola_anp_va_en_singular():
    texto = build_anp_text({**ZAPOPAN, "anp_num_anp": "1"})
    assert "registra 1 área natural protegida." in texto


def test_sin_humedales_el_parrafo_termina_en_las_anp():
    texto = build_anp_text({**ZAPOPAN, "anp_pct_humedales": "0.00"})
    assert texto.endswith("registra 8 áreas naturales protegidas")


def test_sin_anp_no_cambia():
    texto = build_anp_text({**ZAPOPAN, "anp_num_anp": "0", "anp_superficie_anp": "0"})
    assert texto == (
        "El municipio no registra áreas naturales protegidas dentro de su territorio. "
        "Los humedales abarcan 0.35 \\% del territorio municipal"
    )
