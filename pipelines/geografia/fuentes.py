CITAS = {
    "wind_atlas": (
        "Technical University of Denmark (DTU Wind) y el World Bank Group. "
        "Global Wind Atlas",
        "2026",
    ),
    "geoespacial_municipal": ("información geoespacial municipal", "2026"),
    "geologia": ("INEGI. Conjunto de datos vectoriales Geológicos serie I", "1988"),
    "edafologia": (
        r"INEGI. Carta edafológica escala 1:250\,000 Serie III",
        "2025",
    ),
    "topografia": (
        r"INEGI. Conjunto nacional de información topográfica a escala 1:50\,000",
        "2025",
    ),
    "topografia_corta": (r"INEGI. Topografía 1:50\,000", "2025"),
    "cem": ("INEGI. Continuo de Elevaciones Mexicano 4.0", "2025"),
    "cuencas": ("CONAGUA. Disponibilidad en cuencas hidrológicas", "2023"),
    "aguas_superficiales": ("CONAGUA. Ordenamiento de aguas superficial", "2023"),
    "acuiferos": (
        "CONAGUA. Disponibilidad media anual de aguas subterráneas",
        "2024",
    ),
    "condicion_acuiferos": ("CONAGUA. Condición de acuíferos", "2023"),
    "smn": ("SMN. Información Estadística Climatológica", "1995-2025"),
    "usv": (
        "INEGI. Conjunto de datos vectoriales de uso del suelo y vegetación Serie VII",
        "2018",
    ),
    "landsat": ("USGS. Landsat Collection 2 Level-2 Science Products", "2025"),
    "anp": ("CONANP. Áreas Naturales Protegidas", "2025"),
    "humedales": ("CONAGUA. Inventario Nacional de Humedales", "2021"),
    "mapa_jalisco": ("IIEG. Mapa General del Estado de Jalisco", "2012"),
    "itur": ("INEGI. Índice Territorial Urbano-Rural (ITUR)", "2025"),
    "clues": (
        "Dirección General de Información en Salud. "
        "Clave Única de Establecimientos de Salud",
        "2025",
    ),
    "siged": (
        "Sistema de Información y Gestión Educativa (SIGED). Consulta de escuelas",
        "2025",
    ),
    "marco_geo": ("INEGI. Marco Geoestadístico", "2025"),
    "denue": ("INEGI. DENUE", "2025"),
    "sener": ("SENER. Mapa de Hidrocarburos", "2025"),
}

TEMAS = {
    "wind": ["wind_atlas"],
    "sintesis": ["geoespacial_municipal"],
    "geologia": ["geologia"],
    "edafologia": ["edafologia"],
    "topografia": ["topografia", "cem"],
    "cuencas": ["cuencas", "aguas_superficiales"],
    "acuiferos": ["acuiferos", "condicion_acuiferos"],
    "temperatura": ["smn"],
    "precipitacion": ["smn"],
    "clima": ["smn"],
    "usv": ["usv"],
    "ndvi": ["landsat"],
    "ndwi": ["landsat"],
    "anp": ["anp", "humedales"],
    "sequia": ["landsat"],
    "erosion_pot": ["smn", "edafologia", "cem", "mapa_jalisco"],
    "erosion_efe": ["smn", "edafologia", "cem", "mapa_jalisco", "usv"],
    "itur": ["itur"],
    "salud": ["clues"],
    "educacion": ["siged"],
    "espacios": ["marco_geo"],
    "energia": ["denue", "topografia_corta", "sener"],
}

ANIO_TITULO = {
    "wind": "wind_atlas",
    "sintesis": "geoespacial_municipal",
    "geologia": "geologia",
    "edafologia": "edafologia",
    "topografia": "topografia",
    "cuencas": "cuencas",
    "acuiferos": "condicion_acuiferos",
    "temperatura": "smn",
    "precipitacion": "smn",
    "clima": "smn",
    "usv": "usv",
    "ndvi": "landsat",
    "ndwi": "landsat",
    "anp": "anp",
    "sequia": "landsat",
    "erosion_pot": "edafologia",
    "erosion_efe": "edafologia",
    "itur": "itur",
    "salud": "clues",
    "educacion": "siged",
    "espacios": "marco_geo",
    "energia": "denue",
}


ANIO_MAPA = {
    "base": "2025",
    "geologia": "geologia",
    "edafologia": "edafologia",
    "pendientes": "topografia",
    "cuencas": "cuencas",
    "acuiferos": "condicion_acuiferos",
    "temperatura": "2025",
    "precipitacion": "smn",
    "clima": "smn",
    "usv": "usv",
    "ndvi": "landsat",
    "ndwi": "landsat",
    "anp": "anp",
    "sequia": "landsat",
    "erosion_pot": "edafologia",
    "erosion_efe": "edafologia",
    "itur": "itur",
    "salud": "clues",
    "educacion": "siged",
    "espacios": "marco_geo",
    "energia": "denue",
}


def _anio(clave):
    if clave in CITAS:
        return CITAS[clave][1]
    return clave


def _cita(clave):
    texto, anio = CITAS[clave]
    return f"{texto}, {anio}."


def _pie(claves):
    citas = [_cita(clave) for clave in claves]
    if len(citas) == 1:
        return f"Fuente: & IIEG, con base en {citas[0]}"
    cuerpo = "\\\\\n & ".join(citas)
    return f"Fuente: IIEG, con base en & {cuerpo}"


def build_fuentes_context():
    return {
        "ge_fuente": {tema: _pie(claves) for tema, claves in TEMAS.items()},
        "ge_anio": {tema: CITAS[clave][1] for tema, clave in ANIO_TITULO.items()},
        "ge_anio_mapa": {
            mapa: _anio(clave) for mapa, clave in ANIO_MAPA.items() if clave
        },
    }
