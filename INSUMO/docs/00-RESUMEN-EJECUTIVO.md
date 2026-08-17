# Repositorio de Criterios · Fiscalía CONAF
## Resumen ejecutivo

**Qué es.** Una biblioteca de criterio jurídico: busca, ordena cronológicamente y entrega
material trazado sobre lo que la Corporación ha dicho respecto de una materia, con cita literal
verificada y declaración explícita de lo que falta.

**Qué no es.** No es un gestor documental —ese rol lo cumple CeroPapel— ni un sistema de gestión
de trabajo. Y no concluye: entrega el andamiaje, el juicio jurídico es del abogado.

---

## El problema

Reconstruir la historia de un criterio es lento, tedioso y **riesgoso**, porque el abogado no
puede afirmar que tiene todo el material. Ese es el punto: no es un problema de velocidad de
búsqueda, es un problema de **completitud demostrable**.

## La respuesta

Nadie puede demostrar que tiene todo lo escrito en el mundo. Sí se puede demostrar que se tiene
**todo aquello a lo que el corpus apunta**, y listar exactamente lo que falta. Eso convierte una
inquietud sin límite en una lista corta y accionable.

---

## Estado del prototipo

Corre sobre los **20 documentos reales** de la carpeta `Pronunciamientos`. Sin datos de ejemplo.

| | |
|---|---|
| Documentos indexados | **20** |
| Pasajes recuperables | **285** (14,3× frente a un criterio por documento) |
| Referencias detectadas | **37**, todas resueltas o declaradas |
| Vacíos declarados | **36**, de los cuales **12 son doctrina externa** |
| Normas en índice único | **155** entradas, 8 confirmadas en ficha y texto |
| Verificaciones automáticas | **22** — 20 en verde, 2 como cola de adjudicación humana |

## Hallazgos que el prototipo produjo sobre el corpus real

1. **El corpus está casi desconectado de sí mismo.** De 37 referencias, **solo 1** apunta a otro
   documento de la carpeta. Todo lo demás que sostiene el razonamiento vive fuera.
2. **Falta la autoridad que más pesa.** El **Dictamen CGR E33624/2020** —naturaleza jurídica de
   CONAF— es invocado por 4 pronunciamientos y no está en el repositorio. El único documento de
   Contraloría presente no lo cita ningún otro: está huérfano.
3. **Impacto normativo con fecha.** El MM 3129/2022 se funda íntegramente en la Ley 19.628,
   sustituida por la Ley 21.719 el **1 de diciembre de 2026**.
4. **Tensión de criterio sin resolver** entre MM 3320/2026 y MM 3400/2022 sobre la vigencia de
   la obligación de reforestar.
5. **Dos consultas abiertas** que no constituyen criterio: OF 440/2026 y OF 444/2026.
6. **Recuperación por término:** de 14 términos que un abogado teclearía, antes funcionaba 1;
   ahora funcionan 14.

---

## Principio rector

> **Nada se afirma que no pueda comprobarse contra el texto fuente.**

La herramienta no pide que se le crea: publica el resultado de correr 22 verificaciones
deterministas que cualquiera puede reejecutar. Si una de las bloqueantes falla, el índice no se
publica.

## Qué se necesita de Fiscalía

Dos definiciones que ninguna verificación puede inventar:

1. **Banco de consultas de referencia** — ~30 consultas con resultados esperados y prohibidos.
   Una tarde de trabajo de un abogado; es la curaduría de mayor apalancamiento del proyecto.
2. **Partición del vocabulario de materias** — «Gestión de personas» es demasiado ancha para el
   corpus: mezcla jornada, régimen estatutario, remuneraciones y viviendas.

## Índice de esta documentación

| Documento | Para quién |
|---|---|
| `01-ESPECIFICACION-FUNCIONAL.md` | Fiscalía y desarrollo |
| `02-MODELO-DE-DATOS.md` | Desarrollo |
| `03-REGLAS-DE-CALIDAD.md` | Fiscalía y desarrollo |
| `04-CANALIZACION-DE-INGESTA.md` | Desarrollo |
| `05-TESAURO-Y-VOCABULARIO.md` | Fiscalía (curaduría) |
| `06-PLAN-DE-IMPLEMENTACION.md` | Jefatura |
| `07-HALLAZGOS-DEL-CORPUS.md` | Fiscalía |
| `08-BITACORA-DE-DEFECTOS.md` | Desarrollo — por qué existe cada regla |
