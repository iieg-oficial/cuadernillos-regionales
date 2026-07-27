ORDINALES = {
    1: "el subsector más importante",
    2: "los dos subsectores más importantes",
    3: "los tres subsectores más importantes",
}

MAX_SUBSECTORES = 3
ND = "\\ND"


def _join_subsectores(nombres):
    if len(nombres) == 1:
        return f"el de {nombres[0]}"
    return ", ".join(f"el de {n}" for n in nombres[:-1]) + f" y el de {nombres[-1]}"


def build_subsectores_text(subsectores, municipio, anio, pct, aportacion):
    principales = list(subsectores)[:MAX_SUBSECTORES]

    if not principales:
        return (
            f"En {anio} el INEGI reservó por confidencialidad el desglose por "
            f"subsector del valor agregado censal bruto del municipio de "
            f"{municipio}, por lo que únicamente se presenta el total."
        )

    sujeto = ORDINALES[len(principales)]
    verbo_ser = "fue" if len(principales) == 1 else "fueron"

    frase = (
        f"En {anio} {sujeto} en la generación de valor agregado censal bruto "
        f"en el municipio de {municipio} {verbo_ser} "
        f"{_join_subsectores(principales)}"
    )

    if ND in (pct, aportacion) or not pct or not aportacion:
        return f"{frase}."

    verbo_generar = "generó el" if len(principales) == 1 else "generaron en conjunto el"

    return (
        f"{frase}, que {verbo_generar} {pct} o {aportacion} "
        f"millones de pesos del total del valor agregado censal bruto registrado "
        f"en {anio} en el municipio."
    )


def build_mayor_crecimiento_text(
    subsector, aportacion_anterior, aportacion_actual, variacion, anio_anterior, anio
):
    datos = [subsector, aportacion_anterior, aportacion_actual, variacion]
    if not all(datos) or ND in datos:
        return ""

    return (
        f"El subsector de {subsector} fue el que registró el mayor crecimiento "
        f"real pasando de {aportacion_anterior} millones de pesos en "
        f"{anio_anterior} a {aportacion_actual} millones de pesos en {anio}, "
        f"representando una variación del {variacion} durante dicho periodo."
    )
