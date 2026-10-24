# coipo_criterio_fiscalia — Repositorio de Criterios de Fiscalía CONAF

Paquete de implementación (diseño, código de referencia y prototipo) de una **biblioteca de criterio jurídico** para Fiscalía:
busca y ordena cronológicamente lo que la Corporación ha dicho sobre una materia, con cita literal verificada contra el texto fuente
y con los vacíos declarados. **Localiza y ordena; no concluye**: el juicio jurídico es del abogado.

Estado: **insumo / prototipo**, no un servicio en producción. VERIFICADO en el repo: no hay `package.json`, `requirements.txt`, `Dockerfile`,
endpoints ni variables de entorno; el esquema PostgreSQL existe pero el repo no muestra que esté poblado (INFERIDO).
Corre sobre 20 pronunciamientos reales (carpeta `INSUMO/datos/texto-extraido/`).

## Estructura

| Ruta | Contenido |
|---|---|
| `INSUMO/LEEME.md` | Presentación original del paquete y principio rector |
| `INSUMO/docs/00..08-*.md` | Resumen ejecutivo, especificación funcional, modelo de datos, 22 reglas de calidad, ingesta, tesauro, plan, hallazgos del corpus, bitácora de defectos |
| `INSUMO/codigo/` | `nucleo.py`, `tesauro.py`, `dataset.py`, `indice.py`, `integridad.py`, `consistencia.py`, `build.py`, `build2.py`, `app.js`, `estilo.css`, `esquema.sql` |
| `INSUMO/prototipo/prototipo-fiscalia-v2.html` | Prototipo autocontenido; se abre en el navegador |
| `INSUMO/datos/` | `indice.json`, `integridad.json`, `consistencia.json`, `verificacion.json` y los 20 textos congelados |
| `insumos/` | `00-PROBLEMA.md`, `01-SOLUCION.md`, `MANIFIESTO.yaml` (formato de la flota COIPO) |
| `.github/workflows/readme.yml` | Llama al generador de README de la flota (`Sud-Austral/coipo_aireadme`, `@v1`) |

Nota: la carpeta `INSUMO/` (mayúsculas) es material del proyecto; `insumos/` (minúsculas) es la documentación de la flota.

## Cómo verlo

Abrir `INSUMO/prototipo/prototipo-fiscalia-v2.html` en el navegador (no requiere servidor).

## Cómo regenerar (según `INSUMO/LEEME.md`; no lo ejecuté)

Requiere Python 3 y `pdftotext` (poppler) para reprocesar PDFs. Los scripts tienen rutas fijas `/tmp/pron/...` (por ejemplo `/tmp/pron/txt`, `/tmp/pron/app`) que hay que ajustar o recrear.

```bash
cd INSUMO/codigo
python3 indice.py        # construye indice.json
python3 integridad.py    # 22 verificaciones; sale con código distinto de 0 si falla una bloqueante
python3 consistencia.py  # auditoría entre vistas (C1-C7)
python3 build2.py        # regenera el prototipo HTML
```

## Estado de las verificaciones (VERIFICADO en `INSUMO/datos/integridad.json`)

22 verificaciones: 20 en verde y 2 avisos (V12, cola de adjudicación de divergencias; V15, normalización de rótulos de normas). Es el resultado guardado, no una corrida nueva.

## Configuración y pruebas

No hay variables de entorno ni suite de pruebas aparte de `integridad.py` y `consistencia.py`, que hacen de compuerta de publicación.

## Datos personales

El corpus contiene nombres, RUN, domicilios y predios (advertencia del propio `INSUMO/docs/06-PLAN-DE-IMPLEMENTACION.md`). Confirmar con Fiscalía que el repositorio puede tener esta visibilidad.

## Documentos

[`insumos/00-PROBLEMA.md`](insumos/00-PROBLEMA.md) · [`insumos/01-SOLUCION.md`](insumos/01-SOLUCION.md) · [`CLAUDE.md`](CLAUDE.md) · [`INSUMO/LEEME.md`](INSUMO/LEEME.md)
