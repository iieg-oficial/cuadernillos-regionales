from sqlalchemy import text

DETALLES = (
    "ge_anp_municipios",
    "ge_cl_clasificaciones",
    "ge_cl_municipios",
    "ge_cu_disponibilidad",
    "ge_cu_ordenamiento",
    "ge_ds_categorias",
    "ge_ds_municipios",
    "ge_ed_municipios",
    "ge_ed_tipos_suelo",
    "ge_edu_centros",
    "ge_ee_categorias",
    "ge_ee_municipios",
    "ge_ep_espacios",
    "ge_er_categorias",
    "ge_er_municipios",
    "ge_geo_municipios",
    "ge_geo_unidades_geologicas",
    "ge_ie_infraestructura",
    "ge_itur_clasificaciones",
    "ge_itur_municipios",
    "ge_ndvi_categorias",
    "ge_ndvi_municipios",
    "ge_ndwi_categorias",
    "ge_ndwi_municipios",
    "ge_pp_municipios",
    "ge_tm_municipios",
    "ge_tp_municipios",
    "ge_tp_pendientes",
    "ge_usv_clasificacion",
    "ge_usv_municipios",
)


def get_region_indicators(session, clave):
    params = {"clave": clave}
    scalars = (
        session.execute(
            text(
                "SELECT * FROM cuadernillos_tab.ge_regiones WHERE clave_region = :clave"
            ),
            params,
        )
        .mappings()
        .one()
    )
    details = {}
    for table in DETALLES:
        query = text(
            f"SELECT * FROM cuadernillos_tab.{table} WHERE clave_region = :clave "
            "ORDER BY orden"
        )
        details[table] = session.execute(query, params).mappings().all()
    return scalars, details
