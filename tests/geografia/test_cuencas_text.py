from pipelines.geografia.helpers.context import build_cuencas_disponibilidad_text


def test_omite_el_cero_cuando_no_hay_disponibilidad():
    texto = build_cuencas_disponibilidad_text("0.00", "100.00")
    assert texto == (
        "Del total de la superficie municipal comprendida en ellas, "
        "100.00 \\% presenta déficit de disponibilidad de agua superficial."
    )


def test_omite_el_cero_cuando_toda_la_superficie_tiene_disponibilidad():
    texto = build_cuencas_disponibilidad_text("100.00", "0.00")
    assert texto == (
        "Del total de la superficie municipal comprendida en ellas, "
        "100.00 \\% presenta disponibilidad de agua superficial."
    )


def test_menciona_ambas_cifras_cuando_las_dos_son_mayores_a_cero():
    texto = build_cuencas_disponibilidad_text("64.86", "35.14")
    assert "64.86 \\% presenta disponibilidad" in texto
    assert "35.14 \\% presenta déficit" in texto


def test_sin_datos_devuelve_cadena_vacia():
    assert build_cuencas_disponibilidad_text(None, None) == ""


def test_ambas_en_cero_devuelve_cadena_vacia():
    assert build_cuencas_disponibilidad_text("0.00", "0.00") == ""


def test_acepta_valores_con_simbolo_de_porcentaje():
    texto = build_cuencas_disponibilidad_text("0.00 \\%", "100.00 \\%")
    assert "100.00 \\% presenta déficit" in texto
