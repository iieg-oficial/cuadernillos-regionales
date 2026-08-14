# Bases de datos

Referencia única de las bases PostgreSQL que alimentan los cuadernillos: cuáles son, qué sección usa
cuál, cómo se configuran y cómo se consultan.

## Una base, un archivo de entorno

Cada base tiene su propio archivo bajo `.env/`, con el mismo juego de variables:

```env
DB_HOST=<host>
DB_PORT=<puerto>
DB_NAME=<base>
DB_USER=<usuario>
DB_PASSWORD=<contraseña>
```

Los valores reales no van en la documentación ni en el repositorio: `.env/` está en `.gitignore` y
solo se versionan las plantillas de `.env.example/`.

`core/settings.py` expone `DatabaseSettings.from_env(nombre)`, que lee `.env/.env.<nombre>`:

```python
settings = DatabaseSettings.from_env("censo_poblacion")   # lee .env/.env.censo_poblacion
```

Cada `Extract` instancia **solo las bases que necesita**. No hay una conexión global ni un pool
compartido.

Los archivos de `.env/` están en `.gitignore`. En `.env.example/` viven las plantillas.

## Qué base usa cada sección

| Sección | Bases |
|---|---|
| Historia | ninguna; lee `assets/catalogs/historia.json` |
| Geografía | `cuadernillos_geo` |
| Demografía | `censo_poblacion`, `intensidad_migratoria`, `marginacion`, `pobreza_multidimensional` |
| Economía | `censos_economicos`, `denue`, `inpc`, `asg_imss`, `agropecuario_siap`, `produccion_ganadera` |
| Gobierno y seguridad | `participacion_ciudadana`, `efipem`, `delitos_fuero_comun`, `conapo` |
| Directorio municipal | ninguna; lee `assets/catalogs/directorios_municipales.json` |

Son **15 bases** en total para un cuadernillo completo. Existe además `.env.fiscalia`, que hoy no usa
ninguna sección.

## Host

El host de cada base se define en su propio `.env`, así que puede apuntar a donde haga falta sin
tocar código. En principio todas pueden vivir en el servidor; algunas apuntaron a `localhost` en su
momento porque aún no estaban publicadas ahí.

Ten presente que una corrida de los 125 municipios consulta cada base 125 veces: no hay caché de
resultados, así que el tiempo total depende de dónde estén y de la latencia hacia ellas.

## Conexión

`core/db.py` es todo lo que hay:

```python
def get_engine(settings): return create_engine(settings.url)
def get_session(settings) -> Session: return Session(get_engine(settings))
```

Cada `Extract` abre su sesión, consulta y la cierra. Se usa SQLAlchemy 2.0.

## Consultas

Viven en `pipelines/<seccion>/queries/`, una carpeta por sección, y solo se crea si la sección usa
PostgreSQL. Un archivo por tema:

```
pipelines/demografia/queries/
  poblacion.py
  marginacion.py
  migracion.py
  pobreza.py
```

Las consultas devuelven filas ya listas para el `Analizer`; el formateo de cifras se hace después, en
el analizer, nunca en SQL.

### Esquemas

Cada base tiene su propia organización interna. Geografía es la más uniforme: todas sus tablas viven
en el esquema `cuadernillos_tab`, declarado como constante en
`pipelines/geografia/queries/tematicas.py`. Las demás usan `public` o esquemas propios como
`ganaderia`, `agropecuario`, `marginacion` o `poblacion`.

### Vistas

Varias secciones consultan vistas, no tablas. Conviene verificar el prefijo antes de escribir la
consulta: en `delitos_fuero_comun` la vista es `vw_delitos_comparables_general`, y usar `v_` en su
lugar devuelve una sección vacía sin error.

## Diagnóstico

Para probar una conexión sin correr el pipeline:

```bash
set -a && . ./.env/.env.cuadernillos_geo && set +a
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\dt cuadernillos_tab.*'
```

Para inspeccionar qué columnas tiene una tabla:

```bash
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  -c "\d cuadernillos_tab.temperatura_hist_texto_resumen"
```

## Qué no está en la base

No todo el contenido del cuadernillo sale de PostgreSQL, y confundirlo lleva a buscar en el lugar
equivocado:

| Dato | Dónde vive |
|---|---|
| Textos de historia y toponimia | `assets/catalogs/historia.json` |
| Directorio municipal | `assets/catalogs/directorios_municipales.json` |
| Regiones y claves de municipio | `assets/catalogs/regions.json` |
| Años y citas de las fuentes | `pipelines/geografia/fuentes.py` |
| Mapas | `assets/maps/`, descargados de Drive |
| Escudos | `assets/escudos_mun_jal/`, descargado de Drive |

El año de cada fuente es **metadato editorial**, no un dato: no varía por fila, cambia con el
cuadernillo y no con los datos, y su texto lleva marcado LaTeX. Por eso vive en el repositorio y no
en la base.
