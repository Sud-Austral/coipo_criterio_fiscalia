# Solución — Biblioteca de criterio con compuertas de verificación

Marcas: VERIFICADO / INFERIDO / `[PENDIENTE]` / `[VERIFICAR]` como en `00-PROBLEMA.md`. Detalle en `INSUMO/docs/`.

## Qué es
Prototipo autocontenido (`INSUMO/prototipo/prototipo-fiscalia-v2.html`) más el código que lo genera y verifica, sobre 20 documentos reales. VERIFICADO. No hay servicio ni dependencias declaradas; el esquema PostgreSQL (`esquema.sql`, 10 tablas) está escrito y no consta que esté poblado (INFERIDO).

## Arquitectura (VERIFICADO, `docs/04`)
Canalización: 01 Depósito (sha256 del PDF) -> 02 Texto congelado por página -> 03 Segmentación en pasajes -> 04 Etiquetado con tesauro y peso de evidencia -> **05a Compuerta de integridad** (22 verificaciones) -> **05b Compuerta de revisión** (firma del abogado) -> 06 Publicación (índice y alertas). Ambas compuertas son bloqueantes.

## Componentes
- `nucleo.py`: normalización, pasajes, identidad canónica de autoridades, referencias, huella del binario.
- `tesauro.py` y `dataset.py`: vocabulario controlado y fichas curadas de los 20 documentos.
- `indice.py`: construye `indice.json`. `integridad.py`: 22 verificaciones (V01 cita literal, V02 pasaje trazado, V03 hash del binario... V12 divergencias, V15 rótulos de normas). `consistencia.py`: auditoría entre vistas C1-C7.
- `build.py`/`build2.py`, `app.js`, `estilo.css`: generan el HTML. La búsqueda del navegador usa el mismo plegado y lematizador que la suite.
- `esquema.sql`: documento, criterio, cita, descriptor, norma, relación y bitácora (se revoca UPDATE/DELETE a PUBLIC sobre la bitácora).

## Flujo de datos
Textos congelados -> `indice.py` -> `indice.json` -> `integridad.py`/`consistencia.py` -> `build2.py` -> HTML. Las rutas de trabajo del código son `/tmp/pron/...` (no comprobé que reproduzca desde el repo).

## Decisiones
- La unidad recuperable es el pasaje, no el documento. Dos niveles de resultado; la ampliación exige descriptor curado.
- Demostrar cierre de citas («todo aquello a lo que el corpus apunta») en vez de prometer exhaustividad.
- Integración prevista con CeroPapel (12 de 20 documentos son impresiones de ese sistema).

## Estado y pendientes
- Prototipo con 20 documentos, 285 pasajes, 37 referencias (cifras de `docs/00`; no recalculadas). Última modificación del repo: 2026-09-07.
- Plan: 4 fases, 18-20 semanas estimadas (`docs/06`); Fase 4 (dossier exportable con certificado de alcance) sin construir.
- Pendientes de Fiscalía: banco de consultas de referencia, partición del vocabulario, adjudicación de V12/V15, definición de anonimización y de quién accede al índice completo.
- No comprobé: ejecución de los scripts ni el contenido jurídico de los 20 textos.
