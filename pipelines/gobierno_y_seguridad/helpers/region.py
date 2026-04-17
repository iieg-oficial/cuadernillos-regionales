from core.utils.municipalities import get_same_region


def filter_region(munis: list[dict], municipio_id: str) -> list[dict]:
    cvegeo_objetivo = f"14{int(municipio_id):03d}"
    region_cvegeos = {f"14{int(m['id']):03d}" for m in get_same_region(municipio_id)}
    region = [m for m in munis if m["cvegeo"] in region_cvegeos]
    region.sort(
        key=lambda m: (0 if m["cvegeo"] == cvegeo_objetivo else 1, int(m["cvegeo"][2:]))
    )

    for row in region:
        row["clave"] = str(int(row["cvegeo"][2:]))
        row["es_objetivo"] = row["cvegeo"] == cvegeo_objetivo

    return region
