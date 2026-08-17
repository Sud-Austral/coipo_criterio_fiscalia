# Bitácora de defectos

Cada defecto encontrado durante la construcción del prototipo, su causa raíz y la regla que
produjo. **Este documento es el más útil para el equipo de desarrollo**: explica por qué existe
cada verificación y qué pasa si se omite.

Todos los defectos se detectaron sobre **20 documentos**. A escala de cientos, ninguno habría sido
visible a ojo.

---

## D1 · Pasajes no contiguos con el fuente

**Síntoma.** V02 falló en 4 de 285 pasajes: el texto mostrado no existía literalmente en el
documento.

**Causa raíz.** Al limpiar los encabezados de impresión que caen a mitad de un pasaje —los que
cruzan un corte de página— el texto resultante dejaba de ser contiguo en el original. Eran citas
que un abogado no habría podido encontrar en el PDF.

**Corrección.** No se parcharon los cuatro casos: se recorta **todo** pasaje al tramo que sí es
contiguo, cerrándolo en límite de oración.

**Regla.** V02 pasó de comprobación a **garantía estructural**. Ya no puede fallar por construcción.

**Lección.** Cuando una verificación falla, la corrección correcta cambia el proceso, no los datos.

---

## D2 · Falsos positivos del tesauro por término genérico

**Síntoma.** «superficie» etiquetaba como *Cabida predial* un texto sobre monumentos naturales;
«conservación» etiquetaba como *Protección de datos* uno sobre recursos forestales.

**Causa raíz.** Un solo término aislado bastaba para asignar materia.

**Corrección.** Peso de evidencia: una frase de varias palabras vale 2, un término aislado vale 1,
el umbral es 2. Una frase basta por sí sola; dos términos distintos también; uno genérico no.

**Lección.** La ambigüedad léxica es la norma, no la excepción, en textos jurídicos.

---

## D3 · Nombres de fuentes normativas dentro del tesauro

**Síntoma.** Buscar `teletrabajo` devolvía un memorándum sobre admisibilidad de Planes de Manejo,
y lo ponía **primero** en la cronología.

**Cadena del error.**
```
teletrabajo → [materia] Gestión de personas → «estatuto administrativo» → MM 2665/2026
```
El MM 2665/2026 cita el Estatuto Administrativo (arts. 61 y 62) para hablar del **deber de
obediencia jerárquica**, no de gestión de personal.

**Causa raíz.** El tesauro contenía nombres de fuentes normativas y de órganos. **Citar una ley no
dice de qué trata un texto.** Además es redundante: la vía «norma» ya existe y es más precisa,
porque distingue el artículo — el DFL 29 art. 91 (viviendas) y el DFL 29 arts. 61-62 (obediencia)
son el mismo cuerpo y materias distintas.

**Corrección.** 18 términos retirados del tesauro.

**Regla → V14.** Ningún término del tesauro puede ser nombre de norma ni de órgano, contrastado
contra el índice de normas del propio corpus. **Al implementarse encontró 2 casos más** que la
depuración manual había pasado por alto.

---

## D4 · Búsqueda que expande en silencio a la materia amplia

**Síntoma.** El mismo del D3, visto desde la búsqueda: un término específico devolvía toda su
materia mezclada en una sola lista cronológica.

**Causa raíz.** No se distinguía si la consulta **nombraba la materia** o era un término dentro
de ella.

**Corrección.** Dos niveles de resultado, separados y rotulados. Además, la ampliación por materia
exige que la materia esté entre los **descriptores curados** del documento.

**Lección.** El sistema *sí* había detectado el problema —marcaba «convergencia 1/5» y avisaba
«alcanzado por una sola vía»— pero seguía poniendo el resultado equivocado primero.
**Un aviso no compensa un orden equivocado.**

---

## D5 · Lematizador que no unificaba singular y plural

**Síntoma.** El tesauro no reconocía «monumento natural» como nombre de la materia
«Monumentos naturales».

**Causa raíz.** Una lista de sufijos agresiva convertía «naturales» en `natur` y «natural» en
`natural`. La lista intentaba resolver morfología **y** derivación a la vez.

**Corrección.** Regla real del español —plural en *-s* tras vocal, *-es* tras consonante— y
separación de responsabilidades:

> **El lematizador resuelve morfología. El tesauro resuelve sinonimia.**
> Mezclarlas en el lematizador produce sobre-derivación y falsos positivos.

Verificado sobre 12 pares: naturales/natural, leyes/ley, raíces/raíz, sin romper bases/base ni
informes/informe.

---

## D6 · Dos vocabularios para las materias

**Síntoma.** La ficha de un documento decía «Jornada y teletrabajo» y el tesauro «Gestión de
personas». Nunca calzaban.

**Causa raíz.** Dos vocabularios en paralelo, creados en momentos distintos.

**Corrección.** Vocabulario único con equivalencias declaradas: 30 nombres sueltos → 18 términos
preferidos.

**Regla → V13.** Todo descriptor curado debe resolver a un término preferido del tesauro.

**Nota de curaduría.** La normalización **perdió precisión**: «Jornada y teletrabajo» era mejor
descriptor que «Gestión de personas». El sistema lo delata solo, marcando esos documentos con
convergencia 1/5. La partición correcta de esa materia es decisión de Fiscalía.

---

## D7 · Dos fuentes para las normas

**Síntoma.** La vista Normas usaba 77 normas curadas; los pasajes traían 48 extraídas del texto;
**coincidían 10**.

**Causa raíz.** El mismo patrón del D6, en otro campo.

**Corrección.** Índice fusionado de 155 entradas con procedencia declarada: `ficha`, `texto` o
`ambas`, cada una con la página donde el extractor la vio. Ninguna vista lee la lista cruda.

**Regla → C6.**

---

## D8 · Vistas alimentadas por datos escritos a mano

**Síntoma.** Al auditar consistencia entre vistas, **5 de 7 en rojo**.

**Casos reales.**
- Las líneas de criterio dibujaban eslabones sin relación declarada en ninguna ficha: el gráfico
  era un dibujo, no un dato.
- Una alerta nombraba dos oficios en el texto pero apuntaba solo a uno.
- La vista Normas leía la lista curada mientras los pasajes traían la extraída (D7).

**Corrección.** Relaciones agregadas a las fichas, alertas con referencias múltiples, fuente única
de normas.

**Regla → C1–C7**, incorporadas a la suite.

---

## El patrón

**«Dos fuentes para lo mismo» apareció tres veces** (D6, D7, D8) y las tres se descubrió tarde,
arreglando otra cosa. Un patrón que se repite tres veces no es mala suerte: **es un invariante que
faltaba**.

## Quién encontró qué

| Defecto | Detectado por |
|---|---|
| D1 pasajes no contiguos | **V02**, mecánicamente |
| D2 falsos positivos del tesauro | inspección visual |
| D3 nombres de fuentes (2 casos extra) | **V14**, mecánicamente |
| D4 expansión silenciosa | **usuario final**, mirando la pantalla |
| D5 lematizador | al depurar D4 |
| D6 dos vocabularios | al depurar D4 |
| D7 dos fuentes de normas | **C6**, mecánicamente |
| D8 vistas desfasadas | **C1–C7**, mecánicamente |

Los detectados mecánicamente son **violaciones de un invariante**: se atrapan al 100%, gratis, a
cualquier escala. Los detectados a ojo son **juicios de pertinencia**, donde no hay invariante
evidente.

**La clave del método:** casi todo juicio de pertinencia puede convertirse en invariante si se
encuentra el proxy medible. «¿Este documento trata de teletrabajo?» no tiene invariante; «un
término del tesauro no puede ser el nombre de una ley» sí — y era la causa raíz.
