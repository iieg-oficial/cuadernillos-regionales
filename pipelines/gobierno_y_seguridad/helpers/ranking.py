def rank(munis: list[dict]) -> None:
    for sort_key, rank_key in [
        ("valor_anterior", "lugar_anterior"),
        ("valor_actual", "lugar_actual"),
        ("variacion", "lugar_variacion"),
    ]:
        ranked = sorted(munis, key=lambda x: x[sort_key])
        rank_map = {m["cvegeo"]: i + 1 for i, m in enumerate(ranked)}
        for m in munis:
            m[rank_key] = rank_map[m["cvegeo"]]
