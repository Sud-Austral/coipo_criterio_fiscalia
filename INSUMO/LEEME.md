# Repositorio de Criterios · Fiscalía CONAF
## Paquete de implementación

Generado el 17 de agosto de 2026. Todo el contenido corre sobre los **20 documentos reales** de la
carpeta `Pronunciamientos`; no hay datos de ejemplo.

---

## Por dónde empezar

| Si eres… | Lee |
|---|---|
| **Jefatura** | `docs/00-RESUMEN-EJECUTIVO.md` y `docs/06-PLAN-DE-IMPLEMENTACION.md` |
| **Fiscalía / abogado** | `docs/00`, `docs/01-ESPECIFICACION-FUNCIONAL.md`, `docs/05-TESAURO-Y-VOCABULARIO.md` |
| **Desarrollo** | `docs/02-MODELO-DE-DATOS.md`, `docs/03-REGLAS-DE-CALIDAD.md`, `docs/04-CANALIZACION-DE-INGESTA.md` y sobre todo **`docs/08-BITACORA-DE-DEFECTOS.md`** |

Y abre `prototipo/prototipo-fiscalia-v2.html` en el navegador: no requiere servidor.

---

## Contenido

```
docs/
  00-RESUMEN-EJECUTIVO.md          qué es, qué resuelve, en qué estado está
  01-ESPECIFICACION-FUNCIONAL.md   modelo conceptual, búsqueda, las 7 vistas
  02-MODELO-DE-DATOS.md            esquema PostgreSQL y decisiones de diseño
  03-REGLAS-DE-CALIDAD.md          las 22 verificaciones, una por una
  04-CANALIZACION-DE-INGESTA.md    el pipeline y sus dos compuertas
  05-TESAURO-Y-VOCABULARIO.md      curaduría: reglas y decisiones pendientes
  06-PLAN-DE-IMPLEMENTACION.md     fases, insumos requeridos, riesgos
  07-HALLAZGOS-DEL-CORPUS.md       ficha completa de los 20 documentos
  08-BITACORA-DE-DEFECTOS.md       cada defecto, su causa raíz y la regla que produjo

codigo/
  nucleo.py         normalización, pasajes, identidad canónica, referencias
  tesauro.py        vocabulario controlado y autoridades
  dataset.py        fichas curadas de los 20 documentos
  indice.py         construye el índice completo
  integridad.py     las 22 verificaciones  ← la compuerta de publicación
  consistencia.py   auditoría de consistencia entre vistas (C1–C7)
  build.py          datos de líneas de criterio, alertas, API, fases
  build2.py         genera el prototipo HTML
  app.js            lógica de la interfaz (búsqueda multi-vía, vistas)
  estilo.css        hoja de estilo
  esquema.sql       DDL de PostgreSQL con vistas de consulta

prototipo/
  prototipo-fiscalia-v2.html       autocontenido; abrir en el navegador

datos/
  indice.json            el índice completo generado
  integridad.json        resultado de las 22 verificaciones
  consistencia.json      resultado de la auditoría entre vistas
  texto-extraido/        los 20 textos congelados, base de toda verificación
```

---

## Reproducir

Requiere Python 3 y `pdftotext` (poppler) para reprocesar PDFs.

```bash
cd codigo
python3 indice.py        # construye datos/indice.json
python3 integridad.py    # 22 verificaciones; exit ≠ 0 si alguna bloqueante falla
python3 consistencia.py  # auditoría entre vistas (también la corre integridad.py)
python3 build2.py        # regenera el prototipo HTML
```

Las rutas apuntan a `/tmp/pron/...`; ajústelas al instalar. En producción el índice vive en
PostgreSQL y `integridad.py` es la compuerta que decide si se publica.

---

## Principio rector

> **Nada se afirma que no pueda comprobarse contra el texto fuente.**

- El texto extraído del PDF se **congela** y es la base de toda verificación.
- Cada pasaje es **subcadena literal y contigua** del texto congelado (V02).
- Cada cita se contrasta por **coincidencia exacta** tras normalizar ligaduras, comillas, guiones
  y espacios (V01). Cambiar una palabra la hace fallar.
- El **cierre de citas** no demuestra que esté todo lo escrito en el mundo; demuestra que está
  todo aquello a lo que el corpus apunta, y lista lo que falta.
- El etiquetado por tesauro es una **propuesta con evidencia declarada**, no un hecho.
- La búsqueda del navegador usa **el mismo plegado y lematizador** que valida la suite.

## Límite

**La biblioteca localiza y ordena; no concluye.** El juicio jurídico es del abogado.

## Lo que falta y no puede salir del corpus

1. **Banco de ~30 consultas de referencia** con resultados esperados y prohibidos.
2. **Partición del vocabulario**: «Gestión de personas» es demasiado ancha.
3. **Dossier exportable** con certificado de alcance (Fase 4).
