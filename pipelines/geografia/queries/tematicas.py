from sqlalchemy import text

SCHEMA = "cuadernillos_tab"

TOPICS = [
    "acuiferos_condicion",
    "acuiferos_situacion",
    "anp_humedales_manglares",
    "centrales_electricas",
    "clima_koppen",
    "conducto_l",
    "cuencas_categ",
    "cuencas_clasificac",
    "denue_energia",
    "ductos_no_sistrangas",
    "ductos_sistrangas",
    "edafologia",
    "educacion_nivel",
    "erosion_efectiva",
    "erosion_potencial",
    "espacios_publicos",
    "geologia",
    "itur_index_cat",
    "linea_transm_l",
    "ndvi",
    "ndwi",
    "pendiente_clasificada",
    "predios_centrales_electricas",
    "salud_nivel_atencion",
    "sequia",
    "subestacion",
    "uso_suelo",
    "vientos_dominantes",
]


def _table(topic, suffix):
    if topic not in TOPICS and topic not in (
        "descripcion_general",
        "energia",
    ):
        raise ValueError(f"Unknown topic: {topic}")
    return f"{SCHEMA}.{topic}_{suffix}"


def get_variables_texto(session, topic, municipio):
    tbl = _table(topic, "variables_texto")
    if topic == "descripcion_general":
        col = "dg_nombre"
    elif topic == "vientos_dominantes":
        col = "dg_nombre"
    else:
        col = "nombre"
    stmt = text(f"SELECT * FROM {tbl} WHERE {col} = :mun")
    return session.execute(stmt, {"mun": municipio}).mappings().first()


def get_estadistica_detalle(session, topic, municipio):
    tbl = _table(topic, "estadistica_detalle")
    stmt = text(f"SELECT * FROM {tbl} WHERE nombre = :mun ORDER BY orden_pct")
    try:
        return [
            dict(r) for r in session.execute(stmt, {"mun": municipio}).mappings().all()
        ]
    except Exception:
        session.rollback()
        stmt = text(f"SELECT * FROM {tbl} WHERE nombre = :mun")
        return [
            dict(r) for r in session.execute(stmt, {"mun": municipio}).mappings().all()
        ]


def get_estadistica_resumen(session, topic, municipio):
    tbl = _table(topic, "estadistica_resumen")
    stmt = text(f"SELECT * FROM {tbl} WHERE nombre = :mun")
    return session.execute(stmt, {"mun": municipio}).mappings().first()


def get_cobertura_municipal(session, topic, municipio):
    tbl = _table(topic, "cobertura_municipal")
    stmt = text(f"SELECT * FROM {tbl} WHERE nombre = :mun")
    return session.execute(stmt, {"mun": municipio}).mappings().first()
