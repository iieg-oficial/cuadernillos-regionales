from pipelines.geografia.fuentes import (
    CITAS,
    anios_desde_datos,
    build_fuentes_context,
)


def test_toma_el_anio_de_la_tabla_de_salud():
    detalle = {"salud_nivel_atencion": [{"anio": 2026}, {"anio": 2026}]}
    assert anios_desde_datos(detalle) == {"clues": "2026"}


def test_ignora_las_filas_sin_anio_y_toma_la_primera_que_lo_trae():
    detalle = {"salud_nivel_atencion": [{"anio": None}, {"anio": 2027}]}
    assert anios_desde_datos(detalle) == {"clues": "2027"}


def test_sin_columna_no_devuelve_nada():
    assert anios_desde_datos({"salud_nivel_atencion": [{"conteo": 3}]}) == {}
    assert anios_desde_datos({}) == {}


def test_el_anio_de_los_datos_gana_sobre_el_catalogo():
    ctx = build_fuentes_context({"clues": "2026"})
    assert ctx["ge_anio"]["salud"] == "2026"
    assert ctx["ge_anio_mapa"]["salud"] == "2026"
    assert ctx["ge_fuente"]["salud"].endswith("Establecimientos de Salud, 2026.")


def test_sin_dato_cae_al_catalogo():
    ctx = build_fuentes_context()
    respaldo = CITAS["clues"][1]
    assert ctx["ge_anio"]["salud"] == respaldo
    assert ctx["ge_fuente"]["salud"].endswith(f"Establecimientos de Salud, {respaldo}.")


def test_no_toca_los_demas_temas():
    ctx = build_fuentes_context({"clues": "2026"})
    assert ctx["ge_anio"]["educacion"] == CITAS["siged"][1]
    assert ctx["ge_fuente"]["educacion"].endswith(f"escuelas, {CITAS['siged'][1]}.")
