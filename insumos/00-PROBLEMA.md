# Problema — Reconstruir la historia de un criterio jurídico con completitud demostrable

Marcas: VERIFICADO = visto en `INSUMO/docs`, código o datos del repo. INFERIDO = deducido. `[PENDIENTE]` lo cierra el área usuaria. `[VERIFICAR]` lo cierra Fiscalía.
Reescrito el 2026-10-24: la versión anterior se hizo sin leer el contenido de `INSUMO/` y contenía errores (decía 15 verificaciones y un GRANT a público).

## Contexto
Fiscalía de CONAF emite pronunciamientos (MM, OF, resoluciones) y también existen dictámenes de Contraloría y decisiones del Consejo para la Transparencia. El paquete `INSUMO/` se construyó sobre 20 documentos reales de la carpeta «Pronunciamientos» (generado el 17-08-2026). VERIFICADO (`INSUMO/LEEME.md`, `docs/00`).

## Qué duele hoy
Reconstruir la historia de un criterio es lento, tedioso y riesgoso porque el abogado no puede afirmar que tiene todo el material. No es un problema de velocidad de búsqueda sino de **completitud demostrable**. VERIFICADO (`docs/00-RESUMEN-EJECUTIVO.md`). Cuánto tarda hoy y quién lo hace: `[PENDIENTE]`.

## Usuarios
Jefatura, Fiscalía / abogados, desarrollo (tabla «Por dónde empezar» del LEEME). Cantidad de usuarios y quién alimenta el sistema: `[PENDIENTE]`.

## Alcance
Búsqueda multi-vía (término, descriptor curado, texto lematizado, norma, grafo de citas), cronología, líneas de criterio, cierre de citas, vacíos declarados, confiabilidad. VERIFICADO (`docs/01`). Siete vistas del prototipo: Consulta, Líneas de criterio, Cierre de citas, Corpus, Normas, Confiabilidad, Arquitectura.

## Fuera de alcance
No es gestor documental (ese rol es de CeroPapel) ni gestor de trabajo, y no concluye ni redacta el informe. VERIFICADO (`docs/00`, `docs/06`).

## Hallazgos del corpus de prueba (según `docs/00`; no los recalculé)
37 referencias de las cuales solo 1 apunta a otro documento del corpus; el Dictamen CGR E33624/2020 es invocado por 4 pronunciamientos y no está en el repo; MM 3129/2022 se funda en la Ley 19.628, sustituida por la Ley 21.719 el 1-12-2026; tensión entre MM 3320/2026 y MM 3400/2022. Toda afirmación jurídica: `[VERIFICAR]`.

## Criterios de éxito
Las 22 verificaciones deterministas pasan; una bloqueante que falle impide publicar. Estado guardado: 20 en verde y 2 avisos (V12, V15). VERIFICADO (`INSUMO/datos/integridad.json`). Pendiente de Fiscalía: banco de ~30 consultas de referencia y partición del vocabulario «Gestión de personas». Quién da por terminado el proyecto: `[PENDIENTE]`.

## Datos personales
El corpus contiene nombres, RUN, domicilios y predios. Desde el 2026-12-01 aplica la Ley 21.719 a la propia aplicación (control de acceso, trazabilidad, plazos de conservación, evaluación de impacto). Falta definir qué campos se anonimizan. `[VERIFICAR]` si corresponde que este repositorio tenga la visibilidad actual.
