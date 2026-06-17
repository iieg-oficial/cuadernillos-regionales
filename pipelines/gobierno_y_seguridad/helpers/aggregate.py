from collections import defaultdict

POR_CADA = 100_000


def aggregate(
    raw: list[dict], anio_anterior: int, anio_actual: int, pob_map: dict
) -> list[dict]:
    counts = defaultdict(dict)
    names = {}
    for row in raw:
        cvegeo = str(row["cvegeo"])
        counts[cvegeo][int(row["anio"])] = row["total"]
        if row["municipio"]:
            names[cvegeo] = row["municipio"]

    result = []
    for cvegeo, year_counts in counts.items():
        cve_mun = int(cvegeo[2:])
        pob_ant = pob_map.get((cve_mun, anio_anterior))
        pob_act = pob_map.get((cve_mun, anio_actual))
        total_ant = year_counts.get(anio_anterior, 0)
        total_act = year_counts.get(anio_actual, 0)
        tasa_ant = total_ant / pob_ant * POR_CADA if pob_ant else None
        tasa_act = total_act / pob_act * POR_CADA if pob_act else None
        if tasa_ant and tasa_act is not None:
            variacion = round((tasa_act - tasa_ant) / tasa_ant * 100, 2)
        else:
            variacion = 0.0
        result.append(
            {
                "cvegeo": cvegeo,
                "municipio": names.get(cvegeo, ""),
                "valor_anterior": round(tasa_ant, 2) if tasa_ant is not None else None,
                "valor_actual": round(tasa_act, 2) if tasa_act is not None else None,
                "variacion": variacion,
            }
        )
    return result
