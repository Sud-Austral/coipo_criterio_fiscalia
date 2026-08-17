# Plan de implementación

## Fases

| Fase | Entrega | Contenido | Estimación |
|---|---|---|---|
| **Fase 1** | Repositorio verificable | Ingesta, texto congelado con hash, extracción de pasajes, verificación de citas y las 12 comprobaciones de integridad corriendo en cada carga. | 6–8 semanas |
| **Fase 2** | Recuperación multi-vía | Tesauro con sinónimos, identidad canónica de autoridades, búsqueda por descriptor, texto lematizado, norma y grafo de citas, con convergencia declarada. | 5 semanas |
| **Fase 3** | Cierre de citas y vacíos | Grafo completo, clasificación de referencias, calendario de vigencias y cola de adjudicación de divergencias. | 4 semanas |
| **Fase 4** | Dossier con certificado de alcance | Exportación a Word: cronología, citas verificadas, mapa de concordancias y vacíos declarados. Nunca la conclusión. | 3 semanas |

Total estimado: **18–20 semanas** de desarrollo, en secuencia.

## Qué habilita cada fase

**Fase 1 — Repositorio verificable.** Es el piso: sin citas verificadas y sin las verificaciones
corriendo, nada de lo demás es defendible. Al terminarla, un abogado ya puede consultar el corpus
y confiar en lo que ve.

**Fase 2 — Recuperación multi-vía.** Es donde la herramienta empieza a encontrar lo que el abogado
no sabía que existía. Sobre el corpus de prueba, la recuperación por término pasó de 1/14 a 14/14.

**Fase 3 — Cierre de citas y vacíos.** Es la que responde la pregunta que motivó el proyecto:
«¿puedo afirmar que no me falta nada?».

**Fase 4 — Dossier con certificado de alcance.** Es el entregable. Sin él, el trabajo se rehace a
mano cada vez que hay que escribir un informe.

## Insumos requeridos de Fiscalía

| Insumo | Cuándo | Esfuerzo | Quién |
|---|---|---|---|
| Banco de ~30 consultas de referencia | antes de Fase 2 | una tarde | un abogado |
| Partición del vocabulario de materias | antes de Fase 2 | media jornada | Fiscal + abogados |
| Descriptores curados de los documentos existentes | Fase 1 | ~20 min por documento | abogado responsable |
| Adjudicación de la cola V12 (divergencias) | continuo | minutos por caso | abogado |
| Normalización de rótulos de normas (V15) | Fase 3 | acotado | abogado |

**El banco de consultas es el de mayor apalancamiento.** Es curaduría de consultas, no de párrafos,
y atrapa toda regresión futura.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| El corpus crece y la calidad del etiquetado se degrada sin que nadie lo note | Verificaciones corriendo en cada ingesta + muestreo estadístico de precisión |
| Se agrega una vista que lee de una fuente y muestra otra | Auditoría de consistencia C1–C7 en la suite |
| Alguien reemplaza un PDF y las citas apuntan a otro texto | `sha256` del binario; las citas caen a no verificadas |
| La herramienta se usa para redactar conclusiones | Límite de diseño explícito: el dossier entrega andamiaje, nunca conclusión |
| Datos personales del corpus circulan sin control | Ver más abajo |

## Advertencia sobre datos personales

El corpus contiene nombres, RUN, domicilios, predios y razones sociales — la Decisión CPLT
C7949-21 versa justamente sobre eso. Desde el **1 de diciembre de 2026** le son aplicables a la
propia aplicación las obligaciones de la **Ley 21.719**, con el estándar que fija el MM 4187/2026:

- control de acceso por perfiles y necesidad de conocer
- trazabilidad íntegra de accesos y modificaciones
- plazos de conservación determinados (prohibida la conservación indefinida)
- **evaluación de impacto previa y obligatoria** (art. 15 ter)

Falta definir qué campos se anonimizan en las salidas y quién accede al índice completo. Conviene
resolverlo en la etapa de diseño, no después: es exactamente lo que el propio MM 4187/2026
recomienda.

## Límite de diseño, para dejarlo escrito

> **La biblioteca localiza y ordena; no concluye.**

La respuesta a «¿qué se ha dicho sobre X?» es una cronología con citas verificadas, jerarquía,
fuerza y alcance, más la declaración explícita de lo que **no** está cubierto. El dossier entrega
antecedentes, marco normativo, criterio previo y vacíos — nunca una conclusión redactada.

El juicio jurídico es del abogado. La trazabilidad existe para que pueda ejercerlo sobre material
verificable.
