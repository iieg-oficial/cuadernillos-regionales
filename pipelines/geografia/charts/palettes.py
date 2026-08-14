import logging
import re
import unicodedata

LOGGER = logging.getLogger(__name__)
PALETTE_DIAGNOSTICS = []

MAP_TOPIC_TO_PALETTE = {
    "sequia": "categoria_sequia",
    "clima_koppen": "clasificacion_climatica",
    "uso_suelo": "cobertura_suelo",
    "geologia": "geologia",
    "itur_index_cat": "itur_iieg",
    "ndvi": "ndvi",
    "ndwi": "ndwi",
    "erosion_potencial": "perdidas_potenciales_suelo",
    "erosion_efectiva": "perdidas_suelo",
    "pendiente_clasificada": "rango_pendiente",
    "edafologia": "tipo_suelo",
}

CHART_PALETTES = {
    "categoria_sequia": {
        "Sin sequía": "#1a9641",
        "Anormalmente seco": "#8acc62",
        "Sequía moderada": "#dcf09e",
        "Sequía severa": "#ffdf9a",
        "Sequía extrema": "#f69053",
        "Sequía excepcional": "#d7191c",
    },
    "clasificacion_climatica": {
        "BS1kw": "#525252",
        "BS1hw": "#773a0b",
        "BS1(h')w": "#645e18",
        "BS1(h')hw": "#bc911e",
        "Aw0": "#bc1318",
        "Aw1": "#f32070",
        "A(C)w0": "#f7992b",
        "A(C)w1": "#fbbd2d",
        "A(C)m": "#f9f737",
        "(A)Ca(w0)": "#3c5623",
        "(A)Ca(w1)": "#1a8010",
        "(A)Ca(m)": "#b6c094",
        "(A)Cb(w0)": "#c1dbb5",
        "(A)Cb(w1)": "#76f941",
        "(A)Cb(w2)": "#cef84e",
        "(A)Cb(m)": "#d3f9da",
        "Cb(w0)": "#246df5",
        "Cb(w1)": "#4199f9",
        "Cb(w2)": "#6bc9fd",
        "C(b')(w2)": "#46fbf3",
    },
    "cobertura_suelo": {
        "Agricultura": "#fcfdbd",
        "Asentamiento humano": "#818181",
        "Bosque": "#2b7000",
        "Cuerpo de agua": "#68daef",
        "Otros tipos de vegetación": "#8ebdd7",
        "Pastizal": "#ffd177",
        "Selva": "#e56599",
        "Sin vegetación aparente": "#dfdfdf",
    },
    "geologia": {
        "Aluvial": "#ffff66",
        "Andesita": "#ed2a2a",
        "Andesita-Brecha volcánica intermedia": "#edac2a",
        "Andesita-Toba intermedia": "#e6f2a2",
        "Arenisca": "#ccffd8",
        "Arenisca-Conglomerado": "#addab7",
        "Basalto": "#967171",
        "Basalto-Brecha volcánica básica": "#ed2ea7",
        "Basalto-Toba básica": "#e49e9e",
        "Brecha sedimentaria": "#e6b98c",
        "Brecha volcánica básica": "#ffff99",
        "Brecha volcánica intermedia": "#e6f2a2",
        "Caliza": "#43aef8",
        "Caliza-Limolita": "#98bed8",
        "Caliza-Lutita": "#71acd6",
        "Caliza-Yeso": "#c4eef2",
        "Complejo metamórfico": "#a7a7ff",
        "Conglomerado": "#b7d8cc",
        "Cuerpo de agua": "#00d9ff",
        "Dacita": "#fcbe92",
        "Diorita": "#d7a7ad",
        "Eólico": "#fff7cc",
        "Esquisto": "#ace4c8",
        "Gabro": "#e993be",
        "Granito": "#dbf2e0",
        "Granito-Granodiorita": "#8be6a1",
        "Granodiorita": "#ed2ea7",
        "Granodiorita-Tonalita": "#bc4891",
        "Lacustre": "#ace4c8",
        "Latita": "#ff9d46",
        "Limolita-Arenisca": "#d6fe9a",
        "Litoral": "#ffe7cc",
        "Lutita-Arenisca": "#ace4c8",
        "Monzonita": "#ed1186",
        "Palustre": "#fff2cc",
        "Pórfido riolítico": "#ffe0e8",
        "Residual": "#fff1b8",
        "Riodacita": "#fec529",
        "Riodacita-Toba ácida": "#fe9c29",
        "Riolita": "#c1745a",
        "Riolita-Brecha volcánica ácida": "#c1635a",
        "Riolita-Toba ácida": "#d5a294",
        "Toba ácida": "#f8d2d2",
        "Toba ácida-Brecha volcánica ácida": "#ffd1b3",
        "Toba básica": "#ffefd8",
        "Toba básica-Brecha volcánica básica": "#ffd8ea",
        "Toba intermedia": "#fff4c6",
        "Traquita": "#cc4d36",
        "Volcanoclástico": "#85a885",
        "Volcanosedimentaria": "#b9d5b6",
        "Yeso": "#e0e9eb",
    },
    "itur_iieg": {
        "Rural": "#52a97c",
        "Rural transitorio": "#a3eac1",
        "Transición": "#f6d071",
        "Urbano transitorio": "#ef906c",
        "Urbano": "#c95f5b",
    },
    "ndvi": {
        "Sin vegetación aparente (<= 0.22)": "#c62320",
        "Vegetación muy escasa (0.22 - 0.35)": "#f78462",
        "Vegetación escasa (0.35 - 0.50)": "#f7dea3",
        "Vegetación moderada (0.50 - 0.65)": "#98ab76",
        "Vegetación densa (> 0.65)": "#47632a",
    },
    "ndwi": {
        "Vegetación muy seca (<= -0.10)": "#b93961",
        "Vegetación seca (-0.10 - -0.05)": "#f28aaa",
        "Condición hídrica baja (-0.05 - 0.05)": "#e1e1e1",
        "Condición hídrica moderada (0.05 - 0.15)": "#a1c2ed",
        "Alta humedad en vegetación (> 0.15)": "#4060c8",
    },
    "perdidas_potenciales_suelo": {
        "<= 0 No susceptible": "#2b83ba",
        "0 - 5 Erosión muy baja": "#74b6ad",
        "5 - 10 Erosión baja": "#b7e2a8",
        "10 - 25 Erosión leve": "#e7f5b7",
        "25 - 50 Erosión moderada": "#fee8a4",
        "50 - 100 Erosión grave": "#fdba6e",
        "100 - 200 Erosión muy grave": "#ed6e43",
        "> 200 Erosión extrema": "#d7191c",
    },
    "perdidas_suelo": {
        "<= 0 No susceptible": "#2b83ba",
        "0 - 5 Erosión muy baja": "#74b6ad",
        "5 - 10 Erosión baja": "#b7e2a8",
        "10 - 25 Erosión leve": "#e7f5b7",
        "25 - 50 Erosión moderada": "#fee8a4",
        "50 - 100 Erosión grave": "#fdba6e",
        "100 - 200 Erosión muy grave": "#ed6e43",
        "> 200 Erosión extrema": "#d7191c",
    },
    "rango_pendiente": {
        "0 - 2%": "#efeae0",
        "2 - 5%": "#c4c0ac",
        "5 - 10%": "#ae9663",
        "10 - 15%": "#a46f5a",
        "15 - 30%": "#8e3f46",
        "Más de 30%": "#4c0001",
    },
    "tipo_suelo": {
        "Vertisol": "#face9b",
        "Umbrisol": "#cc82ad",
        "Technosol": "#dfc5a8",
        "Solonetz": "#f4f7db",
        "Solonchak": "#f9f189",
        "Regosol": "#fddddc",
        "Planosol": "#fbd080",
        "Phaeozem": "#f5d4c2",
        "Nitisol": "#71b88a",
        "Luvisol": "#c6d347",
        "Lixisol": "#dee387",
        "Leptosol": "#b9b2ac",
        "Kastanozem": "#edaa84",
        "Gleysol": "#d6cfc7",
        "Fluvisol": "#afd5c2",
        "Durisol": "#f19e43",
        "Chernozem": "#df6e37",
        "Cambisol": "#f19b99",
        "Calcisol": "#fef6cf",
        "Cuerpo de agua": "#36c3e9",
        "Arenosol": "#f3e952",
        "Andosol": "#d6aac9",
        "Alisol": "#449442",
        "Acrisol": "#aac963",
    },
}

TOPIC_CATEGORY_ALIASES = {
    "ndvi": {
        "sin_vegetacion": "Sin vegetación aparente (<= 0.22)",
        "vegetacion_muy_escasa": "Vegetación muy escasa (0.22 - 0.35)",
        "vegetacion_escasa": "Vegetación escasa (0.35 - 0.50)",
        "vegetacion_moderada": "Vegetación moderada (0.50 - 0.65)",
        "vegetacion_densa": "Vegetación densa (> 0.65)",
    },
    "ndwi": {
        "vegetacion_muy_seca": "Vegetación muy seca (<= -0.10)",
        "vegetacion_seca": "Vegetación seca (-0.10 - -0.05)",
        "condicion_hidrica_baja": "Condición hídrica baja (-0.05 - 0.05)",
        "condicion_hidrica_moderada": "Condición hídrica moderada (0.05 - 0.15)",
        "alta_humedad_en_vegetacion": "Alta humedad en vegetación (> 0.15)",
    },
    "pendiente_clasificada": {
        "0_a_2": "0 - 2%",
        "0_2": "0 - 2%",
        "mayor_a_2_y_hasta_5": "2 - 5%",
        "mayor_2_y_5": "2 - 5%",
        "2_a_5": "2 - 5%",
        "2_5": "2 - 5%",
        "mayor_a_5_y_hasta_10": "5 - 10%",
        "mayor_5_y_10": "5 - 10%",
        "5_a_10": "5 - 10%",
        "5_10": "5 - 10%",
        "mayor_a_10_y_hasta_15": "10 - 15%",
        "mayor_10_y_15": "10 - 15%",
        "10_a_15": "10 - 15%",
        "10_15": "10 - 15%",
        "mayor_a_15_y_hasta_30": "15 - 30%",
        "mayor_15_y_30": "15 - 30%",
        "15_a_30": "15 - 30%",
        "15_30": "15 - 30%",
        "mayor_a_30": "Más de 30%",
        "mayor_30": "Más de 30%",
        "mas_de_30": "Más de 30%",
        "30": "Más de 30%",
    },
    "erosion_potencial": {
        "0": "<= 0 No susceptible",
        "no_susceptible": "<= 0 No susceptible",
        "0_no_susceptible": "<= 0 No susceptible",
        "menor_igual_0_no_susceptible": "<= 0 No susceptible",
        "mayor_0_y_menor_5": "0 - 5 Erosión muy baja",
        "0_a_5": "0 - 5 Erosión muy baja",
        "0_5": "0 - 5 Erosión muy baja",
        "5_a_10": "5 - 10 Erosión baja",
        "5_10": "5 - 10 Erosión baja",
        "10_a_25": "10 - 25 Erosión leve",
        "10_25": "10 - 25 Erosión leve",
        "25_a_50": "25 - 50 Erosión moderada",
        "25_50": "25 - 50 Erosión moderada",
        "50_a_100": "50 - 100 Erosión grave",
        "50_100": "50 - 100 Erosión grave",
        "100_a_200": "100 - 200 Erosión muy grave",
        "100_200": "100 - 200 Erosión muy grave",
        "mayor_200": "> 200 Erosión extrema",
        "mas_de_200": "> 200 Erosión extrema",
        "200": "> 200 Erosión extrema",
    },
    "erosion_efectiva": {
        "0": "<= 0 No susceptible",
        "no_susceptible": "<= 0 No susceptible",
        "0_no_susceptible": "<= 0 No susceptible",
        "menor_igual_0_no_susceptible": "<= 0 No susceptible",
        "mayor_0_y_menor_5": "0 - 5 Erosión muy baja",
        "0_a_5": "0 - 5 Erosión muy baja",
        "0_5": "0 - 5 Erosión muy baja",
        "5_a_10": "5 - 10 Erosión baja",
        "5_10": "5 - 10 Erosión baja",
        "10_a_25": "10 - 25 Erosión leve",
        "10_25": "10 - 25 Erosión leve",
        "25_a_50": "25 - 50 Erosión moderada",
        "25_50": "25 - 50 Erosión moderada",
        "50_a_100": "50 - 100 Erosión grave",
        "50_100": "50 - 100 Erosión grave",
        "100_a_200": "100 - 200 Erosión muy grave",
        "100_200": "100 - 200 Erosión muy grave",
        "mayor_200": "> 200 Erosión extrema",
        "mas_de_200": "> 200 Erosión extrema",
        "200": "> 200 Erosión extrema",
    },
}


def normalize_token(value):
    text = str(value) if value is not None else ""
    text = text.replace("≤", "<=").replace("≥", ">=")
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\bmas de\b", "más de", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmayor que\b", "mayor a", text, flags=re.IGNORECASE)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    text = text.replace("<=", " menor igual ")
    text = text.replace(">=", " mayor igual ")
    text = text.replace(">", " mayor ")
    text = text.replace("<", " menor ")
    text = re.sub(r"\bmas\s+de\b", "mayor", text)
    text = re.sub(r"\bmayor\s+a\b", "mayor", text)
    text = re.sub(r"\bhasta\b", "", text)
    text = re.sub(r"\ba\b", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def normalize_category_key(topic_key, value):
    if topic_key == "clima_koppen":
        text = str(value) if value is not None else ""
        text = text.replace("’", "'").replace("`", "'")
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"\s+", "", text)
        return text.strip().lower()
    return normalize_token(value)


def topic_palette_lookup(topic_key):
    palette_name = MAP_TOPIC_TO_PALETTE.get(topic_key)
    palette = CHART_PALETTES.get(palette_name, {})
    return {
        normalize_category_key(topic_key, category): color
        for category, color in palette.items()
    }


def _palette_entries(topic_key):
    palette_name = MAP_TOPIC_TO_PALETTE.get(topic_key)
    palette = CHART_PALETTES.get(palette_name, {})
    return palette_name, palette


def has_topic_palette(topic_key):
    _, palette = _palette_entries(topic_key)
    return bool(palette)


def clear_palette_diagnostics():
    PALETTE_DIAGNOSTICS.clear()


def get_palette_diagnostics():
    return list(PALETTE_DIAGNOSTICS)


def resolve_topic_color(topic_key, category, fallback_color):
    palette_name, palette = _palette_entries(topic_key)
    normalized = normalize_category_key(topic_key, category)
    status = "category_not_found"
    matched_label = None
    color = None
    used_fallback = False

    if category in palette:
        matched_label = category
        color = palette[matched_label]
        status = "coincidencia exacta"
    else:
        normalized_lookup = {
            normalize_category_key(topic_key, label): label for label in palette
        }
        if normalized in normalized_lookup:
            matched_label = normalized_lookup[normalized]
            color = palette[matched_label]
            status = "coincidencia tras normalización"
        else:
            alias_label = TOPIC_CATEGORY_ALIASES.get(topic_key, {}).get(normalized)
            if alias_label in palette:
                matched_label = alias_label
                color = palette[matched_label]
                status = "alias explícito"

    if color is None:
        color = fallback_color
        used_fallback = True
        LOGGER.warning(
            "Sin color de paleta para tema=%s categoria=%s; usando fallback=%s",
            topic_key,
            category,
            fallback_color,
        )

    PALETTE_DIAGNOSTICS.append(
        {
            "tema": topic_key,
            "clave_paleta": palette_name,
            "categoria_recibida": category,
            "categoria_normalizada": normalized,
            "categoria_esperada": matched_label,
            "color_resuelto": color,
            "estado": status,
            "uso_fallback": used_fallback,
        }
    )
    return color
