-- Año del corte de CLUES en la tabla de detalle de unidades de salud.
-- El pipeline lo lee con anios_desde_datos() y con él arma el título del cuadro,
-- el del mapa y el pie. Correr en cada base antes de desplegar.
ALTER TABLE cuadernillos_tab.salud_nivel_atencion_estadistica_detalle
  ADD COLUMN IF NOT EXISTS anio integer;

UPDATE cuadernillos_tab.salud_nivel_atencion_estadistica_detalle
   SET anio = 2026
 WHERE anio IS NULL;
