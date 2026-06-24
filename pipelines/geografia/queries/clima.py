from sqlalchemy import text

SCHEMA = "cuadernillos_tab"

MONTHS = [
    "ENE",
    "FEB",
    "MAR",
    "ABR",
    "MAY",
    "JUN",
    "JUL",
    "AGO",
    "SEP",
    "OCT",
    "NOV",
    "DIC",
    "ANUAL",
]


def get_temperatura_long(session, municipio):
    stmt = text(f"SELECT * FROM {SCHEMA}.temperatura_hist_long WHERE municipio = :mun")
    return [dict(r) for r in session.execute(stmt, {"mun": municipio}).mappings().all()]


def get_temperatura_resumen(session, municipio):
    stmt = text(
        f"SELECT * FROM {SCHEMA}.temperatura_hist_texto_resumen WHERE municipio = :mun"
    )
    return session.execute(stmt, {"mun": municipio}).mappings().first()


def get_precipitacion_long(session, municipio):
    stmt = text(
        f"SELECT * FROM {SCHEMA}.precipitacion_hist_long WHERE municipio = :mun"
    )
    return [dict(r) for r in session.execute(stmt, {"mun": municipio}).mappings().all()]


def get_precipitacion_resumen(session, municipio):
    tbl = f"{SCHEMA}.precipitacion_hist_texto_resumen"
    stmt = text(f"SELECT * FROM {tbl} WHERE municipio = :mun")
    return session.execute(stmt, {"mun": municipio}).mappings().first()


def get_wind_frecuencia(session, cve_mun):
    stmt = text(
        f"SELECT * FROM {SCHEMA}.global_wind_frecuencia_municipal WHERE cve_mun = :cve"
    )
    return session.execute(stmt, {"cve": cve_mun}).mappings().first()


def get_municipio_nombre(session, municipio):
    tbl = f"{SCHEMA}.descripcion_general_variables_texto"
    stmt = text(f"SELECT dg_nombre, dg_clave_geo FROM {tbl} WHERE dg_nombre = :mun")
    return session.execute(stmt, {"mun": municipio}).mappings().first()


def get_all_municipios(session):
    tbl = f"{SCHEMA}.descripcion_general_variables_texto"
    stmt = text(f"SELECT dg_nombre, dg_clave_geo FROM {tbl} ORDER BY dg_nombre")
    return [dict(r) for r in session.execute(stmt).mappings().all()]
