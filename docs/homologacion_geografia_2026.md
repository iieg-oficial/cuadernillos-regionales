# Homologación de Geografía y medio ambiente — plantilla regional 2026

## Alcance
- Archivo base: `geografia.tex.j2` suministrado por el usuario; no es el archivo que había comenzado a editar Codex.
- Referencia: borrador DOCX institucional; PDF consultado como referencia de disposición de cuadros.
- Se mantuvo el orden temático de la plantilla original y el apartado «Sequía».
- No se efectuó renderizado, compilación, consultas, cálculos, ni generación de mapas/gráficas.
- Los contratos de datos regionales todavía deben implementarse en los analizadores en una etapa posterior.
- Los bloques originales de gráficas y mapas conservan sus condiciones, macros y variables de imagen; se cambiaron solamente las referencias regionales en títulos.

## Inventario de cuadros incorporados

Los títulos de este inventario conservan los marcadores del borrador para su trazabilidad; en la plantilla todos los nombres regionales utilizan `nombre_region`, conforme a la correspondencia siguiente.
| ID de revisión | Tema | Columnas | Etiqueta de referencia | Lista de filas |
|---|---|---:|---|---|
| D01 | Síntesis geoespacial del territorio de la región <<ig_nombre_region>> | 2 | `tabla_ge_sintesis` | Filas explícitas |
| D04 | Geología de la región <<ge_nombre_region>> | 3 | `tabla_ge_geologia` | `ge_geo_unidades_geologicas` |
| D05 | Unidad predominante y diversidad geológica de los municipios de la región <<ge_nombre_region>> | 4 | `tabla_ge_geo_municipios` | `ge_geo_municipios` |
| D06 | Edafología de la región <<ed_nombre_region>> | 3 | `tabla_ge_edafologia` | `ge_ed_tipos_suelo` |
| D07 | Tipo de suelo predominante y diversidad edafológica de los municipios de la región <<ed_nombre_region>> | 4 | `tabla_ge_ed_municipios` | `ge_ed_municipios` |
| D02 | Topografía y pendientes de la región <<tp_nombre_region>> | 3 | `tabla_ge_pendientes` | `ge_tp_pendientes` |
| D03 | Topografía y pendientes de los municipios de la región <<tp_nombre_region>> | 3 | `tabla_ge_tp_municipios` | `ge_tp_municipios` |
| D14 | Disponibilidad de aguas superficiales en cuencas hidrológicas de la región <<cu_nombre_region>> | 3 | `tabla_ge_cuencas` | `ge_cu_disponibilidad` |
| D15 | Ordenamientos de aguas superficiales en cuencas hidrológicas de la región <<cu_nombre_region>> | 3 | `tabla_ge_cu_ordenamiento` | `ge_cu_ordenamiento` |
| D16 | Disponibilidad de aguas subterráneas en acuíferos de la región <<ac_nombre_region>> | 3 | `tabla_ge_acuiferos` | Filas explícitas |
| D17 | Condición de los acuíferos de la región <<ac_nombre_region>> | 3 | `tabla_ge_ac_condicion` | Filas explícitas |
| D08 | Temperatura mensual y anual de la región <<te_nombre_region>> | 4 | `tabla_ge_temperatura` | Filas explícitas |
| D09 | Temperaturas mínima, media y máxima promedio de los municipios de la región <<te_nombre_region>> | 4 | `tabla_ge_tm_municipios` | `ge_tm_municipios` |
| D10 | Precipitación media mensual y acumulada de la región <<pr_nombre_region>> | 4 | `tabla_ge_precipitacion` | Filas explícitas |
| D11 | Precipitación acumulada anual de los municipios de la región <<pr_nombre_region>> | 2 | `tabla_ge_pp_municipios` | `ge_pp_municipios` |
| D12 | Clima de la región <<cl_nombre_region>> | 3 | `tabla_ge_clima` | `ge_cl_clasificaciones` |
| D13 | Tipo de clima predominante y diversidad climática de los municipios de la región <<cl_nombre_region>> | 4 | `tabla_ge_cl_municipios` | `ge_cl_municipios` |
| D20 | Uso de suelo y vegetación de la región <<us_nombre_region>> | 3 | `tabla_ge_uso_suelo` | `ge_usv_clasificacion` |
| D21 | Uso predominante de los municipios de la región  <<us_nombre_region>> | 6 | `tabla_ge_usv_municipios` | `ge_usv_municipios` |
| D22 | NDVI promedio de la región <<nv_nombre_region>> | 3 | `tabla_ge_ndvi` | `ge_ndvi_categorias` |
| D23 | Porcentaje de vegetación moderada y densa de los municipios de la región  <<nv_nombre_region>> | 2 | `tabla_ge_ndvi_municipios` | `ge_ndvi_municipios` |
| D24 | NDWI promedio de la región <<nw_nombre_region>> | 3 | `tabla_ge_ndwi` | `ge_ndwi_categorias` |
| D25 | Porcentaje de condición moderada y alta de humedad en vegetación de los municipios de la región <<nw_nombre_region>> | 2 | `tabla_ge_ndwi_municipios` | `ge_ndwi_municipios` |
| D18 | Áreas naturales protegidas y humedales de la región <<an_nombre_region>> | 3 | `tabla_ge_anp` | Filas explícitas |
| D19 | Porcentaje de superficie protegida y de humedales de los municipios de la región <<an_nombre_region>> | 3 | `tabla_ge_anp_municipios` | `ge_anp_municipios` |
| D26 | NDDI promedio de la región <<sq_nombre_region>> | 3 | `tabla_ge_sequia` | `ge_ds_categorias` |
| D27 | Porcentaje de las categorías de mayor sequedad de los municipios de la región <<sq_nombre_region>> | 2 | `tabla_ge_ds_municipios` | `ge_ds_municipios` |
| D28 | Erosión potencial de la región <<ep_nombre_region>> | 3 | `tabla_ge_erosion_pot` | `ge_er_categorias` |
| D29 | Erosión potencial de los municipios de la región <<ep_nombre_region>> | 3 | `tabla_ge_er_municipios` | `ge_er_municipios` |
| D30 | Erosión efectiva de la región <<ee_nombre_region>> | 3 | `tabla_ge_erosion_ef` | `ge_ee_categorias` |
| D31 | Erosión efectiva de los municipios de la región <<ee_nombre_region>> | 3 | `tabla_ge_ee_municipios` | `ge_ee_municipios` |
| D32 | Índice Territorial Urbano-Rural de la región <<it_nombre_region>> | 3 | `tabla_ge_itur` | `ge_itur_clasificaciones` |
| D33 | Índice Territorial Urbano-Rural de los municipios de la región <<it_nombre_region>> | 4 | `tabla_ge_itur_municipios` | `ge_itur_municipios` |
| D34 | Unidades de salud de la región <<sa_nombre_region>> | 3 | `tabla_ge_salud` | Filas explícitas |
| D35 | Centros educativos de la región <<ce_nombre_region>> | 4 | `tabla_ge_educacion` | `ge_edu_centros` |
| D36 | Espacios públicos de la región <<sp_nombre_region>> | 3 | `tabla_ge_espacios` | `ge_ep_espacios` |
| D37 | Red de alta tensión de la región <<en_nombre_region>> | 2 | `tabla_ge_energia` | Filas explícitas |
| D38 | Unidades económicas relacionadas con energías de la región <<en_nombre_region>> | 3 | `tabla_ge_ie_establecimientos` | `ge_ie_infraestructura` |

## Correspondencia de variables del borrador al contrato de la plantilla

La correspondencia que sigue es nominal y semántica de plantilla; **no valida que el productor actual entregue valores regionales**. Se reutilizan nombres originales cuando el indicador corresponde al mismo concepto, pero su cálculo y alcance geográfico deberán actualizarse después.

| Marcador del borrador | Variable canónica |
|---|---|
| `ig_nombre_region` | `nombre_region` |
| `ig_ubicacion_general` | `ge_dg_ubicacion_general` |
| `ig_numero_municipios` | `ge_dg_numero_municipios` |
| `ig_municipios_integrantes` | `ge_dg_municipios_integrantes` |
| `ig_superficie_regional_km2` | `ge_dg_superficie_region_km2` |
| `ig_porcentaje_superficie_estatal` | `ge_dg_porcentaje_superficie_estatal` |
| `ig_municipio_mayor_superficie` | `ge_dg_municipio_mayor_superficie` |
| `ig_superficie_municipio_mayor_km2` | `ge_dg_superficie_municipio_mayor_km2` |
| `ig_municipio_menor_superficie` | `ge_dg_municipio_menor_superficie` |
| `ig_superficie_municipio_menor_km2` | `ge_dg_superficie_municipio_menor_km2` |
| `ig_altitud_minima_regional` | `ge_dg_altitud_minima_region` |
| `ig_altitud_maxima_regional` | `ge_dg_altitud_maxima_region` |
| `ig_municipio_altitud_minima` | `ge_dg_municipio_altitud_minima` |
| `ig_altitud_minima_lat` | `ge_dg_altitud_minima_lat` |
| `ig_altitud_minima_lon` | `ge_dg_altitud_minima_lon` |
| `ig_municipio_altitud_maxima` | `ge_dg_municipio_altitud_maxima` |
| `ig_altitud_maxima_lat` | `ge_dg_altitud_maxima_lat` |
| `ig_altitud_maxima_lon` | `ge_dg_altitud_maxima_lon` |
| `ig_municipio_altitud_media_mayor` | `ge_dg_municipio_altitud_media_mayor` |
| `ig_altitud_media_mayor` | `ge_dg_altitud_media_mayor` |
| `ig_municipio_altitud_media_menor` | `ge_dg_municipio_altitud_media_menor` |
| `ig_altitud_media_menor` | `ge_dg_altitud_media_menor` |
| `ig_pendiente_predominante` | `ge_tp_dominante` |
| `ig_porcentaje_pendiente_predominante` | `ge_tp_dominante_pct` |
| `ig_clima_predominante` | `ge_cl_tipo_predominante` |
| `ig_porcentaje_clima_predominante` | `ge_cl_pct_predominante` |
| `ig_temperatura_media_anual` | `ge_tm_media_anual` |
| `ig_precipitacion_anual` | `ge_p_acumulada_anual` |
| `ig_direccion_viento_dominante` | `ge_dg_viento_predom` |
| `ig_frecuencia_viento_dominante` | `ge_dg_viento_predom_fr` |
| `ig_geologia_predominante` | `ge_geo_dominante` |
| `ig_porcentaje_geologia_predominante` | `ge_geo_dominante_pct` |
| `ig_suelo_predominante` | `ge_ed_dominante` |
| `ig_porcentaje_suelo_predominante` | `ge_ed_dominante_pct` |
| `ge_nombre_region` | `nombre_region` |
| `ge_unidad_predominante` | `ge_geo_dominante` |
| `ge_porcentaje_predominante` | `ge_geo_dominante_pct` |
| `ge_pct_unidad_predominante_estado` | `ge_geo_pct_unidad_predominante_estado` |
| `ge_unidad_segunda` | `ge_geo_secundario` |
| `ge_porcentaje_segunda` | `ge_geo_secundario_pct` |
| `ge_municipio_diversidad_mayor` | `ge_geo_municipio_diversidad_mayor` |
| `ge_municipio_diversidad_mayor_indice` | `ge_geo_municipio_diversidad_mayor_indice` |
| `ge_municipio_diversidad_menor` | `ge_geo_municipio_diversidad_menor` |
| `ge_municipio_diversidad_menor_indice` | `ge_geo_municipio_diversidad_menor_indice` |
| `ed_nombre_region` | `nombre_region` |
| `ed_suelo_predominante` | `ge_ed_dominante` |
| `ed_porcentaje_predominante` | `ge_ed_dominante_pct` |
| `ed_pct_suelo_predominante_estado` | `ge_ed_pct_suelo_predominante_estado` |
| `ed_suelo_segundo` | `ge_ed_secundario` |
| `ed_porcentaje_segundo` | `ge_ed_secundario_pct` |
| `ed_municipio_diversidad_mayor` | `ge_ed_municipio_diversidad_mayor` |
| `ed_municipio_diversidad_mayor_indice` | `ge_ed_municipio_diversidad_mayor_indice` |
| `ed_municipio_diversidad_menor` | `ge_ed_municipio_diversidad_menor` |
| `ed_municipio_diversidad_menor_indice` | `ge_ed_municipio_diversidad_menor_indice` |
| `tp_nombre_region` | `nombre_region` |
| `tp_pendiente_predominante` | `ge_tp_dominante` |
| `tp_porcentaje_pendiente_predominante` | `ge_tp_dominante_pct` |
| `tp_pendiente_segunda` | `ge_tp_secundario` |
| `tp_porcentaje_pendiente_segunda` | `ge_tp_secundario_pct` |
| `tp_pct_mayor_30_region` | `ge_tp_pct_mayor_30_region` |
| `tp_pct_mayor_30_estado` | `ge_tp_pct_mayor_30_estado` |
| `tp_lugar_estatal_pendiente_fuerte_texto` | `ge_tp_lugar_estatal_pendiente_fuerte_texto` |
| `tp_municipio_mayor_pendiente_fuerte` | `ge_tp_municipio_mayor_pendiente_fuerte` |
| `tp_porcentaje_mayor_pendiente_fuerte` | `ge_tp_porcentaje_mayor_pendiente_fuerte` |
| `tp_municipio_menor_pendiente_fuerte` | `ge_tp_municipio_menor_pendiente_fuerte` |
| `tp_porcentaje_menor_pendiente_fuerte` | `ge_tp_porcentaje_menor_pendiente_fuerte` |
| `tp_municipio_mayor_pendiente_suave` | `ge_tp_municipio_mayor_pendiente_suave` |
| `tp_porcentaje_mayor_pendiente_suave` | `ge_tp_porcentaje_mayor_pendiente_suave` |
| `cu_nombre_region` | `nombre_region` |
| `cu_cuencas_presentes` | `ge_cu_nombres_cuencas` |
| `cu_pct_con_disponibilidad` | `ge_cu_pct_con_disponibilidad` |
| `cu_pct_sin_disponibilidad` | `ge_cu_pct_sin_disponibilidad` |
| `cu_municipio_mayor_disponibilidad` | `ge_cu_municipio_mayor_disponibilidad` |
| `cu_pct_municipio_mayor_disponibilidad` | `ge_cu_pct_municipio_mayor_disponibilidad` |
| `cu_municipio_menor_disponibilidad` | `ge_cu_municipio_menor_disponibilidad` |
| `cu_pct_municipio_menor_disponibilidad` | `ge_cu_pct_municipio_menor_disponibilidad` |
| `cu_ordenamiento_predominante` | `ge_cu_ordenamiento_predominante` |
| `cu_pct_ordenamiento_predominante` | `ge_cu_pct_ordenamiento_predominante` |
| `ac_nombre_region` | `nombre_region` |
| `ac_acuiferos_presentes` | `ge_ac_nombres_acuiferos` |
| `ac_pct_con_disponibilidad` | `ge_ac_pct_con_disponibilidad` |
| `ac_pct_sin_disponibilidad` | `ge_ac_pct_sin_disponibilidad` |
| `ac_pct_sobreexplotado` | `ge_ac_pct_sobreexplotado` |
| `ac_pct_no_sobreexplotado` | `ge_ac_pct_no_sobreexplotado` |
| `ac_municipio_mayor_sobreexplotacion` | `ge_ac_municipio_mayor_sobreexplotacion` |
| `ac_pct_municipio_mayor_sobreexplotacion` | `ge_ac_pct_municipio_mayor_sobreexplotacion` |
| `ac_municipio_menor_sobreexplotacion` | `ge_ac_municipio_menor_sobreexplotacion` |
| `ac_pct_municipio_menor_sobreexplotacion` | `ge_ac_pct_municipio_menor_sobreexplotacion` |
| `ac_pct_sobreexplotado_estado` | `ge_ac_pct_sobreexplotado_estado` |
| `ac_sup_con_disponibilidad` | `ge_ac_sup_con_disponibilidad` |
| `ac_sup_sin_disponibilidad` | `ge_ac_sup_sin_disponibilidad` |
| `ac_sup_no_sobreexplotado` | `ge_ac_sup_no_sobreexplotado` |
| `ac_sup_sobreexplotado` | `ge_ac_sup_sobreexplotado` |
| `te_nombre_region` | `nombre_region` |
| `te_temperatura_media_anual` | `ge_tm_media_anual` |
| `te_mes_minimo` | `ge_t_meses_menor_temp` |
| `te_temperatura_minima_mes` | `ge_tm_minima_mes` |
| `te_mes_maximo` | `ge_t_meses_mayor_temp` |
| `te_temperatura_maxima_mes` | `ge_tm_maxima_mes` |
| `te_municipio_media_mayor` | `ge_tm_municipio_media_mayor` |
| `te_media_mayor_municipal` | `ge_tm_media_mayor_municipal` |
| `te_municipio_media_menor` | `ge_tm_municipio_media_menor` |
| `te_media_menor_municipal` | `ge_tm_media_menor_municipal` |
| `te_temperatura_media_estatal` | `ge_tm_temperatura_media_estatal` |
| `pr_nombre_region` | `nombre_region` |
| `pr_precipitacion_anual` | `ge_p_acumulada_anual` |
| `pr_mes_menor` | `ge_p_mes_menos_lluvia` |
| `pr_precipitacion_mes_menor` | `ge_p_media_menos_lluvia` |
| `pr_mes_mayor` | `ge_p_mes_mas_lluvia` |
| `pr_precipitacion_mes_mayor` | `ge_p_media_mas_lluvia` |
| `pr_municipio_mayor` | `ge_pp_municipio_mayor` |
| `pr_precipitacion_municipio_mayor` | `ge_pp_precipitacion_municipio_mayor` |
| `pr_municipio_menor` | `ge_pp_municipio_menor` |
| `pr_precipitacion_municipio_menor` | `ge_pp_precipitacion_municipio_menor` |
| `pr_precipitacion_estatal` | `ge_pp_precipitacion_estatal` |
| `cl_fuente_cartografica` | `ge_cl_fuente_cartografica` |
| `cl_nombre_region` | `nombre_region` |
| `cl_clima_predominante` | `ge_cl_tipo_predominante` |
| `cl_porcentaje_predominante` | `ge_cl_pct_predominante` |
| `cl_porcentaje_predominante_estado` | `ge_cl_porcentaje_predominante_estado` |
| `cl_clima_segundo` | `ge_cl_secundario` |
| `cl_porcentaje_segundo` | `ge_cl_secundario_pct` |
| `cl_municipio_diversidad_mayor` | `ge_cl_municipio_diversidad_mayor` |
| `cl_municipio_diversidad_mayor_indice` | `ge_cl_municipio_diversidad_mayor_indice` |
| `cl_municipio_diversidad_menor` | `ge_cl_municipio_diversidad_menor` |
| `cl_municipio_diversidad_menor_indice` | `ge_cl_municipio_diversidad_menor_indice` |
| `us_nombre_region` | `nombre_region` |
| `us_cobertura_predominante` | `ge_usv_dominante` |
| `us_porcentaje_predominante` | `ge_usv_dominante_pct` |
| `us_porcentaje_predominante_estado` | `ge_usv_porcentaje_predominante_estado` |
| `us_cobertura_segunda` | `ge_usv_secundario` |
| `us_porcentaje_segunda` | `ge_usv_secundario_pct` |
| `us_municipio_mayor_agricultura` | `ge_usv_municipio_mayor_agricultura` |
| `us_pct_mayor_agricultura` | `ge_usv_pct_mayor_agricultura` |
| `us_municipio_mayor_bosque` | `ge_usv_municipio_mayor_bosque` |
| `us_pct_mayor_bosque` | `ge_usv_pct_mayor_bosque` |
| `us_municipio_mayor_asentamiento` | `ge_usv_municipio_mayor_asentamiento` |
| `us_pct_mayor_asentamiento` | `ge_usv_pct_mayor_asentamiento` |
| `nv_nombre_region` | `nombre_region` |
| `nv_categoria_predominante` | `ge_ndvi_dominante` |
| `nv_porcentaje_predominante` | `ge_ndvi_dominante_pct` |
| `nv_categoria_segunda` | `ge_ndvi_secundario` |
| `nv_porcentaje_segunda` | `ge_ndvi_secundario_pct` |
| `nv_pct_moderada_densa_region` | `ge_ndvi_pct_moderada_densa_region` |
| `nv_pct_moderada_densa_estado` | `ge_ndvi_pct_moderada_densa_estado` |
| `nv_municipio_mayor_moderada_densa` | `ge_ndvi_municipio_mayor_moderada_densa` |
| `nv_pct_mayor_moderada_densa` | `ge_ndvi_pct_mayor_moderada_densa` |
| `nv_municipio_menor_moderada_densa` | `ge_ndvi_municipio_menor_moderada_densa` |
| `nv_pct_menor_moderada_densa` | `ge_ndvi_pct_menor_moderada_densa` |
| `nw_nombre_region` | `nombre_region` |
| `nw_categoria_predominante` | `ge_ndwi_dominante` |
| `nw_porcentaje_predominante` | `ge_ndwi_dominante_pct` |
| `nw_categoria_segunda` | `ge_ndwi_secundario` |
| `nw_porcentaje_segunda` | `ge_ndwi_secundario_pct` |
| `nw_pct_moderada_alta_region` | `ge_ndwi_pct_moderada_alta_region` |
| `nw_pct_moderada_alta_estado` | `ge_ndwi_pct_moderada_alta_estado` |
| `nw_municipio_mayor_moderada_alta` | `ge_ndwi_municipio_mayor_moderada_alta` |
| `nw_pct_mayor_moderada_alta` | `ge_ndwi_pct_mayor_moderada_alta` |
| `nw_municipio_menor_moderada_alta` | `ge_ndwi_municipio_menor_moderada_alta` |
| `nw_pct_menor_moderada_alta` | `ge_ndwi_pct_menor_moderada_alta` |
| `an_nombre_region` | `nombre_region` |
| `an_numero_anp` | `ge_anp_numero_anp` |
| `an_superficie_protegida_ha` | `ge_anp_superficie_protegida_ha` |
| `an_pct_superficie_protegida` | `ge_anp_pct_superficie_protegida` |
| `an_pct_superficie_protegida_estado` | `ge_anp_pct_superficie_protegida_estado` |
| `an_ambito_predominante` | `ge_anp_ambito_predominante` |
| `an_pct_ambito_predominante` | `ge_anp_pct_ambito_predominante` |
| `an_superficie_humedales_ha` | `ge_anp_superficie_humedales_ha` |
| `an_pct_humedales` | `ge_anp_pct_humedales` |
| `an_municipio_mayor_proteccion` | `ge_anp_municipio_mayor_proteccion` |
| `an_pct_municipio_mayor_proteccion` | `ge_anp_pct_municipio_mayor_proteccion` |
| `an_municipio_menor_proteccion` | `ge_anp_municipio_menor_proteccion` |
| `an_pct_municipio_menor_proteccion` | `ge_anp_pct_municipio_menor_proteccion` |
| `an_municipio_mayor_humedales` | `ge_anp_municipio_mayor_humedales` |
| `an_pct_municipio_mayor_humedales` | `ge_anp_pct_municipio_mayor_humedales` |
| `an_sup_federal` | `ge_anp_sup_federal` |
| `an_pct_federal` | `ge_anp_pct_federal` |
| `an_sup_estatal` | `ge_anp_sup_estatal` |
| `an_pct_estatal` | `ge_anp_pct_estatal` |
| `an_sup_municipal` | `ge_anp_sup_municipal` |
| `an_pct_municipal` | `ge_anp_pct_municipal` |
| `an_sup_humedales` | `ge_anp_sup_humedales` |
| `sq_nombre_region` | `nombre_region` |
| `sq_categoria_predominante` | `ge_ds_dominante` |
| `sq_porcentaje_predominante` | `ge_ds_dominante_pct` |
| `sq_categoria_segunda` | `ge_ds_secundario` |
| `sq_porcentaje_segunda` | `ge_ds_secundario_pct` |
| `sq_pct_severa_extrema_excepcional_region` | `ge_ds_pct_severa_extrema_excepcional_region` |
| `sq_pct_severa_extrema_excepcional_estado` | `ge_ds_pct_severa_extrema_excepcional_estado` |
| `sq_municipio_mayor_sequedad` | `ge_ds_municipio_mayor_sequedad` |
| `sq_pct_mayor_sequedad` | `ge_ds_pct_mayor_sequedad` |
| `sq_municipio_menor_sequedad` | `ge_ds_municipio_menor_sequedad` |
| `sq_pct_menor_sequedad` | `ge_ds_pct_menor_sequedad` |
| `ep_nombre_region` | `nombre_region` |
| `ep_categoria_predominante` | `ge_er_dominante_rango` |
| `ep_porcentaje_predominante` | `ge_er_dominante_pct` |
| `ep_categoria_segunda` | `ge_er_secundario_rango` |
| `ep_porcentaje_segunda` | `ge_er_secundario_pct` |
| `ep_pct_mayor_50_region` | `ge_er_pct_mayor_50_region` |
| `ep_municipio_mayor_50` | `ge_er_municipio_mayor_50` |
| `ep_pct_municipio_mayor_50` | `ge_er_pct_municipio_mayor_50` |
| `ep_municipio_menor_50` | `ge_er_municipio_menor_50` |
| `ep_pct_municipio_menor_50` | `ge_er_pct_municipio_menor_50` |
| `ep_pct_mayor_50_estado` | `ge_er_pct_mayor_50_estado` |
| `ee_nombre_region` | `nombre_region` |
| `ee_categoria_predominante` | `ge_ee_dominante_rango` |
| `ee_porcentaje_predominante` | `ge_ee_dominante_pct` |
| `ee_categoria_segunda` | `ge_ee_secundario_rango` |
| `ee_porcentaje_segunda` | `ge_ee_secundario_pct` |
| `ee_pct_mayor_50_region` | `ge_ee_pct_mayor_50_region` |
| `ee_municipio_mayor_50` | `ge_ee_municipio_mayor_50` |
| `ee_pct_municipio_mayor_50` | `ge_ee_pct_municipio_mayor_50` |
| `ee_municipio_menor_50` | `ge_ee_municipio_menor_50` |
| `ee_pct_municipio_menor_50` | `ge_ee_pct_municipio_menor_50` |
| `ee_pct_mayor_50_estado` | `ge_ee_pct_mayor_50_estado` |
| `it_nombre_region` | `nombre_region` |
| `it_categoria_predominante` | `ge_itur_dominante` |
| `it_porcentaje_predominante` | `ge_itur_dominante_pct` |
| `it_categoria_segunda` | `ge_itur_secundario` |
| `it_porcentaje_segunda` | `ge_itur_secundario_pct` |
| `it_pct_urbano_ampliado_region` | `ge_itur_pct_urbano_ampliado_region` |
| `it_pct_urbano_ampliado_estado` | `ge_itur_pct_urbano_ampliado_estado` |
| `it_municipio_mayor_urbano` | `ge_itur_municipio_mayor_urbano` |
| `it_pct_mayor_urbano` | `ge_itur_pct_mayor_urbano` |
| `it_municipio_menor_urbano` | `ge_itur_municipio_menor_urbano` |
| `it_pct_menor_urbano` | `ge_itur_pct_menor_urbano` |
| `sa_nombre_region` | `nombre_region` |
| `sa_total_unidades` | `ge_salud_total_unidades` |
| `sa_total_primer_nivel` | `ge_salud_total_primer_nivel` |
| `sa_total_segundo_nivel` | `ge_salud_total_segundo_nivel` |
| `sa_total_tercer_nivel` | `ge_salud_total_tercer_nivel` |
| `sa_total_otros` | `ge_salud_total_otros` |
| `sa_institucion_mayor` | `ge_salud_institucion_mayor` |
| `sa_unidades_institucion_mayor` | `ge_salud_unidades_institucion_mayor` |
| `sa_institucion_segunda` | `ge_salud_institucion_segunda` |
| `sa_unidades_institucion_segunda` | `ge_salud_unidades_institucion_segunda` |
| `sa_municipio_mayor_unidades` | `ge_salud_municipio_mayor_unidades` |
| `sa_mayor_unidades_municipales` | `ge_salud_mayor_unidades_municipales` |
| `sa_municipio_menor_unidades` | `ge_salud_municipio_menor_unidades` |
| `sa_menor_unidades_municipales` | `ge_salud_menor_unidades_municipales` |
| `sa_pct_primer_nivel` | `ge_salud_pct_primer_nivel` |
| `sa_pct_segundo_nivel` | `ge_salud_pct_segundo_nivel` |
| `sa_pct_tercer_nivel` | `ge_salud_pct_tercer_nivel` |
| `sa_pct_otros` | `ge_salud_pct_otros` |
| `ce_nombre_region` | `nombre_region` |
| `ce_total_centros` | `ge_edu_total_centros` |
| `ce_nivel_mayor` | `ge_edu_nivel_mayor` |
| `ce_centros_nivel_mayor` | `ge_edu_centros_nivel_mayor` |
| `ce_nivel_segundo` | `ge_edu_nivel_segundo` |
| `ce_centros_nivel_segundo` | `ge_edu_centros_nivel_segundo` |
| `ce_total_publicos` | `ge_edu_total_publicos` |
| `ce_total_particulares` | `ge_edu_total_particulares` |
| `ce_pct_publicos` | `ge_edu_pct_publicos` |
| `ce_pct_particulares` | `ge_edu_pct_particulares` |
| `ce_municipio_mayor_centros` | `ge_edu_municipio_mayor_centros` |
| `ce_mayor_centros_municipales` | `ge_edu_mayor_centros_municipales` |
| `ce_municipio_menor_centros` | `ge_edu_municipio_menor_centros` |
| `ce_menor_centros_municipales` | `ge_edu_menor_centros_municipales` |
| `sp_nombre_region` | `nombre_region` |
| `sp_total_espacios` | `ge_ep_total_espacios` |
| `sp_tipo_predominante` | `ge_ep_tipo_predominante` |
| `sp_cantidad_predominante` | `ge_ep_cantidad_predominante` |
| `sp_porcentaje_predominante` | `ge_ep_porcentaje_predominante` |
| `sp_tipo_segundo` | `ge_ep_tipo_segundo` |
| `sp_cantidad_segundo` | `ge_ep_cantidad_segundo` |
| `sp_porcentaje_segundo` | `ge_ep_porcentaje_segundo` |
| `sp_municipio_mayor_espacios` | `ge_ep_municipio_mayor_espacios` |
| `sp_mayor_espacios_municipales` | `ge_ep_mayor_espacios_municipales` |
| `sp_municipio_menor_espacios` | `ge_ep_municipio_menor_espacios` |
| `sp_menor_espacios_municipales` | `ge_ep_menor_espacios_municipales` |
| `en_anio` | `ge_ene_anio` |
| `en_nombre_region` | `nombre_region` |
| `en_total_subestaciones` | `ge_ene_total_subestaciones` |
| `en_km_alta_tension` | `ge_ene_linea_transm_l_km` |
| `en_densidad_alta_tension_region` | `ge_ene_densidad_alta_tension_region` |
| `en_municipio_mayor_densidad_red` | `ge_ene_municipio_mayor_densidad_red` |
| `en_mayor_densidad_red` | `ge_ene_mayor_densidad_red` |
| `en_municipio_menor_densidad_red` | `ge_ene_municipio_menor_densidad_red` |
| `en_menor_densidad_red` | `ge_ene_menor_densidad_red` |
| `en_densidad_alta_tension_estado` | `ge_ene_densidad_alta_tension_estado` |
| `en_tipo_predominante` | `ge_ene_tipo_predominante` |
| `en_cantidad_predominante` | `ge_ene_cantidad_predominante` |
| `en_porcentaje_predominante` | `ge_ene_porcentaje_predominante` |
| `en_tipo_segundo` | `ge_ene_tipo_segundo` |
| `en_cantidad_segundo` | `ge_ene_cantidad_segundo` |
| `en_porcentaje_segundo` | `ge_ene_porcentaje_segundo` |
| `en_municipio_mayor_unidades` | `ge_ene_municipio_mayor_unidades` |
| `en_mayor_unidades_municipales` | `ge_ene_mayor_unidades_municipales` |
| `en_municipio_menor_unidades` | `ge_ene_municipio_menor_unidades` |
| `en_menor_unidades_municipales` | `ge_ene_menor_unidades_municipales` |

## Contratos de listas utilizados por los cuadros

Los nombres de lista existentes se conservaron cuando fue posible. Las listas municipales nuevas son esquemas de presentación pendientes de productor; **no son cálculos implementados**.

| Cuadro | Lista | Campos esperados por fila, en orden |
|---|---|---|
| D04 | `ge_geo_unidades_geologicas` | `roca`, `superficie_ha`, `porcentaje` |
| D05 | `ge_geo_municipios` | `municipio`, `unidad_predominante`, `porcentaje_predominante`, `indice_shannon` |
| D06 | `ge_ed_tipos_suelo` | `tipo_suelo`, `superficie_ha`, `porcentaje` |
| D07 | `ge_ed_municipios` | `municipio`, `suelo_predominante`, `porcentaje_predominante`, `indice_shannon` |
| D02 | `ge_tp_pendientes` | `categoria`, `superficie_ha`, `porcentaje` |
| D03 | `ge_tp_municipios` | `municipio`, `pendiente_hasta_5_pct`, `pendiente_mayor_30_pct` |
| D14 | `ge_cu_disponibilidad` | `categoria`, `superficie_ha`, `porcentaje` |
| D15 | `ge_cu_ordenamiento` | `categoria`, `superficie_ha`, `porcentaje` |
| D09 | `ge_tm_municipios` | `municipio`, `media_anual`, `minima_promedio_anual`, `maxima_promedio_anual` |
| D11 | `ge_pp_municipios` | `municipio`, `precipitacion_anual` |
| D12 | `ge_cl_clasificaciones` | `clasificacion_climatica`, `superficie_ha`, `porcentaje` |
| D13 | `ge_cl_municipios` | `municipio`, `clima_predominante`, `porcentaje_predominante`, `indice_shannon` |
| D20 | `ge_usv_clasificacion` | `grupo`, `superficie_ha`, `porcentaje` |
| D21 | `ge_usv_municipios` | `municipio`, `uso_predominante`, `porcentaje_predominante`, `agricultura_pct`, `bosque_pct`, `asentamientos_pct` |
| D22 | `ge_ndvi_categorias` | `categoria`, `superficie_ha_aj`, `porcentaje` |
| D23 | `ge_ndvi_municipios` | `municipio`, `vegetacion_moderada_densa_pct` |
| D24 | `ge_ndwi_categorias` | `categoria`, `superficie_ha_aj`, `porcentaje` |
| D25 | `ge_ndwi_municipios` | `municipio`, `humedad_moderada_alta_pct` |
| D19 | `ge_anp_municipios` | `municipio`, `superficie_protegida_pct`, `humedales_pct` |
| D26 | `ge_ds_categorias` | `categoria`, `superficie_ha`, `porcentaje` |
| D27 | `ge_ds_municipios` | `municipio`, `sequedad_alta_pct` |
| D28 | `ge_er_categorias` | `categoria`, `superficie_ha`, `porcentaje` |
| D29 | `ge_er_municipios` | `municipio`, `perdida_mayor_50_pct`, `perdida_mayor_100_pct` |
| D30 | `ge_ee_categorias` | `categoria`, `superficie_ha`, `porcentaje` |
| D31 | `ge_ee_municipios` | `municipio`, `perdida_mayor_50_pct`, `perdida_mayor_100_pct` |
| D32 | `ge_itur_clasificaciones` | `categoria`, `superficie_ha`, `porcentaje` |
| D33 | `ge_itur_municipios` | `municipio`, `urbano_ampliado_pct`, `transicion_pct`, `rural_ampliado_pct` |
| D35 | `ge_edu_centros` | `nivel_educativo`, `publico`, `particular`, `total` |
| D36 | `ge_ep_espacios` | `tipo`, `cantidad`, `porcentaje` |
| D38 | `ge_ie_infraestructura` | `tipo_infraestructura`, `cantidad`, `porcentaje` |

## Puntos de integración futura

- Todas las narrativas y cuadros utilizan alcance regional; la procedencia real de los datos deberá verificarse antes de generar cuadernillos.
- Los mapas y gráficas siguen utilizando sus variables de imagen originales. La sustitución de insumos municipales por regionales se realizará en el pipeline posteriormente.
- El inventario de categorías presentado en el DOCX es ilustrativo en varias tablas (`…`); en esos casos se emplean listas, no filas artificiales.
- D34 (Salud) cambia de un detalle por institución/nivel a un resumen por nivel, como en el borrador. D35 (Educación) agrega la columna `total`. D36 (Espacios públicos) requiere cantidades por tipo, no superficies.
- D26–D27 mantienen la denominación editorial «Sequía» y el contrato `ge_ds_*`; verificar la equivalencia metodológica con NDDI antes de producir datos.
- Las fuentes narrativas y de cuadros proceden del borrador; las referencias dinámicas de imágenes y los metadatos `ge_anio.*` conservan los contratos existentes.
- Clima: 1995–2025 conforme al borrador; vientos ERA5 2025 según la decisión previa, con referencia bibliográfica detallada pendiente. Actualizar los productores `ge_anio.wind` y `ge_fuente.wind` al incorporar datos.
- Este artefacto **no está compilado ni renderizado**, por indicación expresa. La revisión actual es únicamente estructural y estática.

## Revisión estática de cierre

- Comparación con `develop` (`d0149495`): 38 cuadros, 16 bloques de gráficas y 21 bloques cartográficos; orden temático, etiquetas originales y bloques de imágenes conservados.
- Delimitadores y anidamiento Jinja2 balanceados, sin funciones ni filtros nuevos.
- Entornos LaTeX balanceados; columnas, proporciones (suma 1.00), encabezados repetidos y extensiones de pies verificados en las 38 tablas.
- Contratos de campos de las 30 listas cotejados con esta documentación; destinos de la correspondencia de variables presentes en la plantilla.
- Corrección estática limitada: separador `&` entre la etiqueta «Fuente:» y el texto en los 38 pies, conforme al macro institucional de dos columnas.
- Sin renderizado, compilación ni ejecución de pipelines; esta revisión no acredita la disponibilidad ni el alcance regional de los datos.
