# coipo_criterio_fiscalia — guía para agentes

Biblioteca de criterio jurídico de Fiscalía CONAF (prototipo + diseño). Visión general en [`README.md`](README.md); problema y solución en [`insumos/`](insumos/).

## Principio rector (no negociable)
**Nada se afirma que no pueda comprobarse contra el texto fuente.** Cada pasaje es subcadena literal del texto congelado (V02); cada cita se contrasta por coincidencia exacta tras normalizar (V01). La herramienta **localiza y ordena; no concluye**. Nunca redactar conclusiones jurídicas ni afirmar vigencia de normas: eso lo cierra Fiscalía.

## Estructura
- `INSUMO/codigo/` — Python sin dependencias declaradas (`nucleo.py` normalización/pasajes/identidad, `tesauro.py`, `dataset.py` fichas curadas de los 20 documentos, `indice.py`, `integridad.py` 22 verificaciones, `consistencia.py` C1-C7, `build.py`/`build2.py` generan el HTML, `app.js`, `estilo.css`, `esquema.sql`).
- `INSUMO/datos/` — salidas generadas (índice, integridad, consistencia, verificación) y los 20 textos congelados. Son la base de toda verificación: no editarlos a mano.
- `INSUMO/prototipo/` — HTML generado por `build2.py`; no editarlo directamente, cambiar `app.js`/`estilo.css`/`build2.py` y regenerar.
- `INSUMO/docs/` — especificación; `08-BITACORA-DE-DEFECTOS.md` explica por qué existe cada regla: leerla antes de tocar `integridad.py`.

## Comandos (de `INSUMO/LEEME.md`; no los ejecuté)
Desde `INSUMO/codigo`: `python3 indice.py`, `python3 integridad.py`, `python3 consistencia.py`, `python3 build2.py`. Necesitan `pdftotext` para reprocesar PDFs.

## Trampas
- Las rutas están fijas a `/tmp/pron/txt` y `/tmp/pron/app` (en `nucleo.py`, `build*.py`, `indice.py`, `consistencia.py`). Los scripts no funcionan tal cual desde el repo en Windows; no cambiarlas sin avisar.
- `build2.py` importa a `build.py`; no consta cuál es la generación vigente del constructor más allá de que el prototipo actual es `v2`.
- Hay dos carpetas: `INSUMO/` (proyecto) e `insumos/` (flota COIPO). No fusionarlas ni cambiar mayúsculas.
- `.github/workflows/readme.yml` delega en `coipo_aireadme@v1`; el `uses:` y `engine_ref` deben coincidir.
- El corpus incluye datos personales: no copiar contenido de los textos a otros documentos, issues o PRs.
- Marcas en `insumos/`: `[PENDIENTE]` lo cierra el área usuaria; `[VERIFICAR]` lo cierra Fiscalía.

## Qué no tocar
Los textos congelados, `datos/*.json` generados y el principio rector. Los defectos ya corregidos están en la bitácora: no reintroducirlos.
