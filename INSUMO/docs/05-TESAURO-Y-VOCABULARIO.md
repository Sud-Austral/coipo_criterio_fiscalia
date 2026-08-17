# Tesauro y vocabulario controlado

Documento de **curaduría**: describe qué mantiene Fiscalía y con qué reglas.

## Estado actual

| | |
|---|---|
| Términos preferidos (materias) | **18** |
| Frases registradas | 161 |
| Términos de una palabra | 87 |
| Equivalencias de descriptores | 12 |
| Autoridades con identidad canónica | 15 |

## Cómo etiqueta

Cada materia agrupa dos clases de término:

- **frases** — expresiones de varias palabras, propias de la materia. **Peso 2**: bastan solas.
- **palabras** — términos de una palabra, distintivos pero ambiguos fuera de contexto.
  **Peso 1**: se exigen dos coincidencias distintas.

**Umbral: 2.** Es lo que impide que «superficie» dispare *Cabida predial* en un texto sobre
monumentos naturales, o que «conservación» dispare *Protección de datos* en uno sobre recursos
forestales. Ambos fallos ocurrieron.

## Las tres reglas duras

### 1. El tesauro no contiene nombres de fuentes ni de órganos
**Citar una ley no dice de qué trata un texto.** «Estatuto administrativo», «Código del Trabajo»,
«Superintendencia del Medio Ambiente» quedan fuera. Para eso está la vía «norma», que además
distingue el artículo — y el artículo es el que decide la materia.

Verificado por **V14**.

### 2. El lematizador resuelve morfología; el tesauro resuelve sinonimia
Singular/plural y nominalizaciones son trabajo del lematizador. Que «araucaria» lleve a
*Monumentos naturales* o «sindicato» a *Gestión de personas* es trabajo del tesauro. Mezclarlos
produce sobre-derivación.

### 3. Un solo vocabulario
Todo descriptor curado debe resolver a un término preferido. Verificado por **V13**.

## Identidad canónica de autoridades

Un mismo dictamen aparece en el corpus escrito de tres formas:

> `E33624` · `33624` · `33.624` — es el **Dictamen CGR E33624/2020**

Sin identidad canónica, quien busca una grafía no encuentra los documentos que usaron las otras, y
el índice inverso la cuenta como tres autoridades distintas. Cada autoridad registra sus variantes
y **V08** comprueba que no colisionen entre sí.

**Pendiente:** extender la identidad canónica a las **normas**. V15 detectó 6 casos donde la ficha
rotula distinto de como el documento cita —«Estatutos CONAF art. 18» frente a «artículo 18 de los
estatutos de la Corporación Nacional Forestal»—. Es el mismo problema un nivel más abajo.

## Cómo se mide si un término sirve

Un término es **diagnóstico** si los documentos que lo contienen pertenecen a la materia que
declara. Se mide contra los descriptores curados a nivel de documento:

```
precisión(término) = documentos que lo contienen Y tienen la materia
                     ─────────────────────────────────────────────────
                             documentos que lo contienen
```

Bajo 0,6 el término no distingue nada y debe retirarse o moverse.

**La economía de esto es el punto:** curar **20 fichas de documento** valida **248 términos**
de tesauro. No hace falta curar párrafos.

## Materias actuales

- **Actos administrativos** — 10 frases, 3 términos
- **Bienes institucionales** — 8 frases, 5 términos
- **Cabida predial** — 13 frases, 5 términos
- **Contratación pública** — 15 frases, 8 términos
- **Fiscalización forestal** — 7 frases, 5 términos
- **Gestión de personas** — 11 frases, 8 términos
- **Límites de competencia** — 6 frases, 2 términos
- **Monumentos naturales** — 10 frases, 10 términos
- **Naturaleza jurídica de CONAF** — 6 frases, 1 términos
- **Planes de manejo** — 7 frases, 4 términos
- **Probidad y conflictos de interés** — 9 frases, 4 términos
- **Procedimiento administrativo** — 8 frases, 4 términos
- **Protección de datos personales** — 17 frases, 8 términos
- **Reforestación y compensación** — 8 frases, 5 términos
- **Remuneraciones** — 6 frases, 4 términos
- **SEIA / RCA / PAS** — 4 frases, 4 términos
- **Transparencia y acceso a la información** — 6 frases, 3 términos
- **Áreas silvestres protegidas** — 10 frases, 4 términos

## Decisiones pendientes de Fiscalía

### 1. Partir «Gestión de personas»
Es demasiado ancha para el corpus: mezcla jornada y teletrabajo, régimen estatutario,
remuneraciones y viviendas fiscales. La normalización del vocabulario **perdió precisión** al
colapsar «Jornada y teletrabajo» dentro de ella — el descriptor original de Fiscalía era mejor.

El sistema lo delata solo: los documentos sobre teletrabajo aparecen con **convergencia 1/5** y el
aviso «revisar su descriptor».

### 2. Banco de consultas de referencia
~30 consultas con resultados esperados y prohibidos. Es curaduría de **consultas**, no de párrafos:
una tarde de trabajo, y atrapa toda regresión futura. Habría evitado que el defecto D4 llegara a
la pantalla.

Formato sugerido:

```yaml
- consulta: teletrabajo
  debe_incluir: [MM-3171-2026, OF-440-2026]
  no_debe_incluir: [MM-2665-2026]
  nota: MM-2665 solo cita el Estatuto Administrativo por obediencia jerárquica
```

## Mantenimiento

Al incorporar documentos nuevos, revisar:
1. Términos que aparecen en muchos pasajes y no están en el tesauro → candidatos a agregar.
2. Términos del tesauro con precisión bajo 0,6 → candidatos a retirar.
3. Materias con más de ~40 documentos → candidatas a partirse.
