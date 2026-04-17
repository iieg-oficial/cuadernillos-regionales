from collections import defaultdict


def aggregate(raw: list[dict], anio_anterior: int, anio_actual: int) -> list[dict]:
    counts = defaultdict(dict)
    names = {}
    for row in raw:
        cvegeo = str(row["cvegeo"])
        counts[cvegeo][int(row["anio"])] = row["total"]
        if row["municipio"]:
            names[cvegeo] = row["municipio"]

    result = []
    for cvegeo, year_counts in counts.items():
        val_ant = year_counts.get(anio_anterior, 0)
        val_act = year_counts.get(anio_actual, 0)
        variacion = round(
            ((val_act - val_ant) / val_ant * 100) if val_ant > 0 else 0.0, 2
        )
        result.append(
            {
                "cvegeo": cvegeo,
                "municipio": names.get(cvegeo, ""),
                "valor_anterior": val_ant,
                "valor_actual": val_act,
                "variacion": variacion,
            }
        )
    return result
