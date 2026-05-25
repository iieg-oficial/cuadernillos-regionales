# Validacion de datos

Queries para validar en DBeaver contra los CSV/Excel fuente.
Reemplazar `{cve_mun}` con la clave del municipio (ej. 39 para Guadalajara)
y `{act_id}` (act_id = 1 año pasado, act_id =  2 el actual) con el id de la actualizacion vigente.


## Número de empresas

Base de datos: `denue`

### Texto

- [ ] `ec_municipio_nombre`: nombre del municipio

```sql
SELECT m.nomgeo
FROM public.cvegeo_municipalities m
WHERE m.cve_mun = {cve_mun} AND m.cve_ent = 14
LIMIT 1;
```

- [ ] `ec_mes_denue_numero_empresas`: mes de la ultima actualizacion del DENUE
- [ ] `ec_anio_denue`: anio de la ultima actualizacion del DENUE

```sql
SELECT id, fecha_actualizacion
FROM public.cat_actualizaciones
ORDER BY fecha_actualizacion DESC
LIMIT 1;
```

- [ ] `ec_unidades_economicas`: total de unidades economicas del municipio

```sql
SELECT COUNT(*) AS total
FROM public.stg_establecimientos e
JOIN public.cat_localidades l ON e.localidad_id = l.id
WHERE e.actualizacion_id = {act_id}
  AND l.municipio_id = {cve_mun}
  AND l.entidad_id = 14;
```

- [ ] `ec_porcentaje_unidades_economicas`: porcentaje que representa del total estatal
- [ ] `ec_posicion_municipio_establecimientos`: lugar en ranking de municipios con mas establecimientos

```sql
WITH conteos AS (
    SELECT
        l.municipio_id,
        COUNT(*) AS total
    FROM public.stg_establecimientos e
    JOIN public.cat_localidades l ON e.localidad_id = l.id
    WHERE e.actualizacion_id = {act_id}
      AND l.entidad_id = 14
    GROUP BY l.municipio_id
),
ranked AS (
    SELECT
        municipio_id,
        total,
        SUM(total) OVER () AS total_estatal,
        ROUND(total * 100.0 / SUM(total) OVER (), 2) AS porcentaje,
        RANK() OVER (ORDER BY total DESC) AS posicion
    FROM conteos
)
SELECT municipio_id, total, total_estatal, porcentaje, posicion
FROM ranked
WHERE municipio_id = {cve_mun};
```

- [ ] `ec_sector_mayor_unidades`: sector con mayor numero de unidades economicas
- [ ] `ec_porcentaje_sector_mayor_unidades`: porcentaje del sector mayor respecto al total municipal
- [ ] `ec_sector_segundo_unidades`: segundo sector
- [ ] `ec_porcentaje_sector_segundo_unidades`: porcentaje del segundo sector
- [ ] `ec_sector_tercer_unidades`: tercer sector
- [ ] `ec_porcentaje_sector_tercer_unidades`: porcentaje del tercer sector

```sql
WITH totales AS (
    SELECT
        s.sector,
        COUNT(*) AS total
    FROM public.stg_establecimientos e
    JOIN public.cat_localidades l ON e.localidad_id = l.id
    JOIN public.cat_sectores s ON e.sector_id = s.id
    WHERE e.actualizacion_id = {act_id}
      AND l.municipio_id = {cve_mun}
      AND l.entidad_id = 14
    GROUP BY s.sector
)
SELECT
    sector,
    total,
    ROUND(total * 100.0 / SUM(total) OVER (), 2) AS porcentaje
FROM totales
ORDER BY total DESC;
```

### Tabla 8. Cantidad de unidades economicas por sector y segun composicion

```sql
SELECT
    s.sector,
    rp.descripcion AS rango_personal,
    COUNT(*) AS total
FROM public.stg_establecimientos e
JOIN public.cat_localidades l ON e.localidad_id = l.id
JOIN public.cat_sectores s ON e.sector_id = s.id
JOIN public.cat_rangos_personal rp ON e.rango_personal_id = rp.id
WHERE e.actualizacion_id = {act_id}
  AND l.municipio_id = {cve_mun}
  AND l.entidad_id = 14
GROUP BY s.sector, rp.descripcion, rp.id
ORDER BY s.sector, rp.id;
```

Validar:

- [ ] Nombre del sector
- [ ] Desglose por rango de personal: 0-5, 6-10, 11-30, 31-50, 51-100, 101-250, 251+
- [ ] Total de unidades economicas del sector
- [ ] Porcentaje del total de unidades economicas
- [ ] `ec_denue_total_r0a5`: suma columna 0 a 5 personas
- [ ] `ec_denue_total_r6a10`: suma columna 6 a 10 personas
- [ ] `ec_denue_total_r11a30`: suma columna 11 a 30 personas
- [ ] `ec_denue_total_r31a50`: suma columna 31 a 50 personas
- [ ] `ec_denue_total_r51a100`: suma columna 51 a 100 personas
- [ ] `ec_denue_total_r101a250`: suma columna 101 a 250 personas
- [ ] `ec_denue_total_r251mas`: suma columna 251 y mas personas
- [ ] La suma de todos los rangos por fila coincide con el total del sector
- [ ] La suma de todos los totales por sector coincide con `ec_unidades_economicas`

## Valor agregado censal bruto

Base de datos: `censos_economicos`

### Texto

- [ ] `ec_anio_ce`: anio de referencia del censo economico (2024)
- [ ] `ec_anio_ce_anterior`: anio de referencia del censo economico anterior (2019)

> Valores fijos en el pipeline: 2024 y 2019.

- [ ] `ec_vacb_total_actual`: VACB total del municipio en 2024
- [ ] `ec_vacb_total_anterior`: VACB total del municipio en 2019

```sql
-- VACB total 2024
SELECT SUM(v.valor_agregado_censal_bruto_mdp) AS vacb_total
FROM public.vw_economico_municipal_2024 v
WHERE v.cve_ent = 14
  AND v.cve_mun = {cve_mun}
  AND v.estrato_id = 1
  AND v.subsector IS NOT NULL
  AND v.subsector != ''
  AND v.valor_agregado_censal_bruto_mdp IS NOT NULL;
```

```sql
-- VACB total 2019
SELECT SUM(valor_agregado_censal_bruto_mdp) AS vacb_total
FROM public.vw_economico_municipal_2019
WHERE cve_ent = 14
  AND cve_mun = {cve_mun}
  AND estrato_id = 1
  AND LENGTH(actividad_codigo) = 3
  AND valor_agregado_censal_bruto_mdp IS NOT NULL;
```

- [ ] `ec_variacion_valor_agregado_censal`: variacion real del VACB entre ambos censos
- [ ] `ec_variacion_vacb_total`: variacion porcentual total

> Se calcula como: `(vacb_total_2024 - vacb_total_2019) / vacb_total_2019 * 100`

- [ ] `ec_subsector_primer_lugar`: subsector con mayor VACB
- [ ] `ec_subsector_segundo_lugar`: segundo subsector con mayor VACB
- [ ] `ec_subsector_tercer_lugar`: tercer subsector con mayor VACB
- [ ] `ec_porcentaje_aportacion_principales_subsectores`: porcentaje conjunto de los 3 principales subsectores
- [ ] `ec_aportacion_principales_subsectores`: monto en pesos de los 3 principales subsectores

```sql
-- Top subsectores por VACB 2024
SELECT
    SPLIT_PART(v.subsector, '.', 1) AS codigo,
    ca.descripcion AS subsector,
    SUM(v.valor_agregado_censal_bruto_mdp) AS vacb
FROM public.vw_economico_municipal_2024 v
JOIN public.cat_actividades_economicas ca
    ON SPLIT_PART(v.subsector, '.', 1) = ca.codigo
    AND ca.censo_id = (SELECT id FROM public.cat_censos WHERE anio = 2024)
    AND ca.codigo_id = 3
WHERE v.cve_ent = 14
  AND v.cve_mun = {cve_mun}
  AND v.estrato_id = 1
  AND v.subsector IS NOT NULL
  AND v.subsector != ''
  AND v.valor_agregado_censal_bruto_mdp IS NOT NULL
GROUP BY SPLIT_PART(v.subsector, '.', 1), ca.descripcion
ORDER BY vacb DESC NULLS LAST;
```

> Los primeros 3 resultados son los subsectores principales.
> El porcentaje conjunto se calcula como: `suma_top3 / vacb_total_2024 * 100`

- [ ] `ec_subsector_mayor_crecimiento`: subsector con mayor crecimiento real
- [ ] `ec_aportacion_anterior_subsector_mayor_crecimiento`: VACB del subsector en el censo anterior
- [ ] `ec_aportacion_subsector_mayor_crecimiento`: VACB del subsector en el censo actual
- [ ] `ec_variacion_porcentual_aportacion_subsector_mayor_crecimiento`: variacion porcentual del subsector

> Se calcula comparando cada subsector entre 2024 y 2019 con el query anterior y el siguiente:

```sql
-- Subsectores por VACB 2019
SELECT
    actividad_codigo AS codigo,
    actividad AS subsector,
    SUM(valor_agregado_censal_bruto_mdp) AS vacb
FROM public.vw_economico_municipal_2019
WHERE cve_ent = 14
  AND cve_mun = {cve_mun}
  AND estrato_id = 1
  AND LENGTH(actividad_codigo) = 3
  AND valor_agregado_censal_bruto_mdp IS NOT NULL
GROUP BY actividad_codigo, actividad
ORDER BY vacb DESC NULLS LAST;
```

> El mayor crecimiento se obtiene cruzando ambos por `codigo`: `(vacb_2024 - vacb_2019) / vacb_2019 * 100`, el de mayor tasa es el resultado.

### Tabla 9. Subsectores con mayor valor agregado censal bruto

> Se construye con los dos queries anteriores (subsectores 2024 y 2019), cruzados por `codigo`.
> Se muestran los 9 subsectores con mayor VACB en 2024, el resto se agrupa como "Otros".

Validar:

- [ ] Nombre del subsector
- [ ] `vacb_anterior`: VACB del censo anterior
- [ ] `vacb_actual`: VACB del censo actual
- [ ] `pct_part`: porcentaje de participacion en el censo actual (`vacb / vacb_total_2024 * 100`)
- [ ] `var_pct`: variacion porcentual entre censos (`(vacb_2024 - vacb_2019) / vacb_2019 * 100`)
- [ ] La suma de los subsectores + "Otros" coincide con los totales

## Empleo

> Pipeline no implementado. Todas las variables se muestran como N/D.

### Trabajadores asegurados en el IMSS

#### Texto

- [ ] `ec_mes_corte_imss`: mes de corte de la informacion del IMSS
- [ ] `ec_anio_corte_imss`: anio de corte
- [ ] `ec_anio_anterior_corte_imss`: anio anterior al corte
- [ ] `ec_dos_anios_atras_corte_imss`: dos anios atras del corte
- [ ] `ec_total_trabajadores_imss`: total de trabajadores asegurados en el municipio
- [ ] `ec_porcentaje_trabajadores_asegurados_jalisco`: porcentaje respecto al total estatal
- [ ] `ec_porcentaje_variacion_asegurados`: variacion anual de trabajadores asegurados
- [ ] `ec_grupo_ec_con_mas_empleos`: grupo economico con mas empleos
- [ ] `ec_num_trabajadores_grupo_mayor`: numero de trabajadores del grupo con mas empleos
- [ ] `ec_porcentaje_trabajadores_grupo_mayor`: porcentaje del grupo con mas empleos

#### Tabla 10. Trabajadores asegurados por grupo economico

- [ ] Nombre del grupo economico
- [ ] `t2`: trabajadores dos anios atras
- [ ] `t1`: trabajadores anio anterior
- [ ] `t0`: trabajadores anio actual
- [ ] `pct_part`: porcentaje de participacion
- [ ] `var_nominal`: variacion nominal entre anio anterior y actual
- [ ] `var_pct`: variacion porcentual entre anio anterior y actual

### Trabajadores asegurados por el IMSS en la region

#### Texto

- [ ] `ec_region`: nombre de la region
- [ ] `ec_posicion_municipio_region`: posicion del municipio en la region
- [ ] `ec_porcentaje_asegurados_region`: porcentaje del municipio en la region

#### Tabla 11. Trabajadores asegurados por municipio en la region

- [ ] Nombre del municipio
- [ ] Total de trabajadores asegurados anio anterior
- [ ] Total de trabajadores asegurados anio actual
- [ ] Porcentaje de participacion en la region
- [ ] Variacion nominal
- [ ] Variacion porcentual
- [ ] El municipio actual aparece resaltado

## Agricultura

Base de datos: `agropecuario_siap`

Reemplazar `{anio}` con el anio de corte (ej. 2024).

### Texto

- [ ] `ec_anio_corte_sagarpa`: anio de corte de la informacion agropecuaria

> Usar el anio mas reciente con datos disponibles:

```sql
SELECT DISTINCT anio
FROM public.stg_agricola
WHERE entidad_id = 14
ORDER BY anio DESC
LIMIT 1;
```

- [ ] `ec_valor_produccion_agricola`: valor de la produccion agricola en millones de pesos

```sql
SELECT
    ROUND(SUM(valor_produccion) / 1000000.0, 2) AS valor_produccion_mdp
FROM public.stg_agricola
WHERE entidad_id = 14
  AND municipio_id = {cve_mun}
  AND anio = {anio};
```

- [ ] `ec_porcentaje_respecto_al_estado_agricola`: porcentaje respecto al total estatal

```sql
WITH estatal AS (
    SELECT SUM(valor_produccion) AS total
    FROM public.stg_agricola
    WHERE entidad_id = 14
      AND anio = {anio}
),
municipal AS (
    SELECT SUM(valor_produccion) AS total
    FROM public.stg_agricola
    WHERE entidad_id = 14
      AND municipio_id = {cve_mun}
      AND anio = {anio}
)
SELECT ROUND(municipal.total * 100.0 / estatal.total, 2) AS porcentaje
FROM municipal, estatal;
```

### Grafica

- [ ] `ec_grafica_agricultura`: grafica de produccion agricola generada correctamente

> Para validar los datos de la grafica, usar la vista:

```sql
SELECT cultivo, SUM(valor_produccion) AS valor_produccion
FROM public.view_agricola_jalisco
WHERE municipio_id = {cve_mun}
  AND anio = {anio}
GROUP BY cultivo
ORDER BY valor_produccion DESC;
```

## Ganaderia

Base de datos: `produccion_ganadera`

Reemplazar `{anio}` con el anio de corte (ej. 2024).

### Texto

- [ ] `ec_valor_produccion_ganado`: valor de la produccion ganadera en millones de pesos

```sql
SELECT
    ROUND(SUM(valor_produccion) / 1000000.0, 2) AS valor_produccion_mdp
FROM public.stg_ganadera
WHERE entidad_id = 14
  AND municipio_id = {cve_mun}
  AND anio = {anio};
```

- [ ] `ec_porcentaje_respecto_al_estado_ganado`: porcentaje respecto al total estatal

```sql
WITH estatal AS (
    SELECT SUM(valor_produccion) AS total
    FROM public.stg_ganadera
    WHERE entidad_id = 14
      AND anio = {anio}
),
municipal AS (
    SELECT SUM(valor_produccion) AS total
    FROM public.stg_ganadera
    WHERE entidad_id = 14
      AND municipio_id = {cve_mun}
      AND anio = {anio}
)
SELECT ROUND(municipal.total * 100.0 / estatal.total, 2) AS porcentaje
FROM municipal, estatal;
```

### Grafica

- [ ] `ec_grafica_ganaderia`: grafica de produccion ganadera generada correctamente

> Para validar los datos de la grafica, usar la vista:

```sql
SELECT especie, producto, SUM(valor_produccion) AS valor_produccion
FROM public.view_ganadera_jalisco
WHERE municipio_id = {cve_mun}
  AND anio = {anio}
GROUP BY especie, producto
ORDER BY valor_produccion DESC;
```
