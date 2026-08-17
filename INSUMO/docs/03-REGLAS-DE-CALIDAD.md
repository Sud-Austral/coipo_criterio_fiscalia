# Reglas de calidad — las 22 verificaciones

La herramienta no pide que se le crea. Publica el resultado de correr verificaciones
deterministas sobre todo el corpus, y cualquiera puede reejecutarlas:

```bash
python3 indice.py        # construye el índice
python3 integridad.py    # 22 verificaciones; exit ≠ 0 si alguna bloqueante falla
```

En producción esto es la **compuerta de publicación**: si una bloqueante falla, el índice no se
publica.

## Las verificaciones

| Código | Título | Qué prueba | Estado | Tipo |
|---|---|---|---|---|
| `V01` | Cita literal verificada | citas contrastadas contra el texto congelado | 20/20 | **bloqueante** |
| `V02` | Pasaje trazado al fuente | pasajes que existen literalmente en su documento | 285/285 | **bloqueante** |
| `V03` | Hash del binario registrado | documentos con sha256 del PDF registrado | 20/20 | **bloqueante** |
| `V04` | Criterio principal indexado | documentos con su criterio principal indexado | 20/20 | **bloqueante** |
| `V05` | Sin documento invisible | documentos con al menos un pasaje recuperable | 20/20 | **bloqueante** |
| `V06` | Materia curada e inferida | documentos con materia curada y materia inferida del texto | 20/20 | **bloqueante** |
| `V07` | Cierre de citas completo | referencias resueltas al corpus o declaradas como vacío | 37/37 | **bloqueante** |
| `V08` | Identidad canónica de autoridades | autoridades sin colisión entre sus variantes de cita | 15/15 | **bloqueante** |
| `V09` | Consistencia cronológica | referencias cuya fecha es anterior a la del documento que las cita | 37/37 | **bloqueante** |
| `V10` | Cobertura multi-vía | documentos alcanzables por dos o más vías independientes | 20/20 | **bloqueante** |
| `V11` | Sin duplicados | documentos sin duplicado de contenido en el índice | 20/20 | **bloqueante** |
| `V12` | Divergencias declaradas | pares con materia común: relación declarada o marcados para revisión | 177/190 | aviso — cola humana |
| `V13` | Vocabulario único | descriptores curados que resuelven a un término preferido | 30/30 | **bloqueante** |
| `V14` | Tesauro sin nombres de fuentes | términos del tesauro que no son nombres de fuentes ni de órganos | 248/248 | **bloqueante** |
| `V15` | Normas de la ficha respaldadas | normas de la ficha cuyo rótulo coincide con la forma en que el documento las cita | 78/84 | aviso — cola humana |
| `C1` | Campos leídos existen en el índice | referencias a campos inexistentes o desfasados | 55/55 | **bloqueante** |
| `C2` | Nodos de líneas apuntan al corpus | documentos citados en las cadenas que existen | 17/17 | **bloqueante** |
| `C3` | Cadenas respaldadas por relaciones de ficha | eslabones consecutivos con relación declarada en el índice | 4/4 | **bloqueante** |
| `C4` | Alertas reflejan el estado del índice | alertas consistentes con los estados calculados | 8/8 | **bloqueante** |
| `C5` | Cifras del texto coinciden con el índice | cifras escritas a mano contrastadas; otras 24 se interpolan del índice | 3/3 | **bloqueante** |
| `C6` | Fuente única para las normas | índice fusionado de 155 entradas, 8 confirmadas en ficha y texto | 1/1 | **bloqueante** |
| `C7` | Materias mostradas están en el tesauro | toda materia visible es un término preferido | 18/18 | **bloqueante** |

**Bloqueantes (20).** Expresan invariantes: algo que siempre debe ser cierto. Se atrapan al 100%,
a cualquier escala, sin intervención humana.

**Avisos (2).** V12 y V15 no son defectos sino **colas de adjudicación**: la máquina propone y un
abogado decide. Marcado un caso, sale de la cola. Son colas que se vacían, no fallas.

---

## Las tres familias

### V01–V11 · Integridad del índice
Que la cita exista literalmente, que el pasaje sea subcadena contigua del fuente, que el binario
tenga hash, que ningún documento quede invisible, que toda referencia esté resuelta o declarada,
que ninguna autoridad tenga identidad duplicada, que nadie cite el futuro, que todo documento sea
alcanzable por dos vías, que no haya duplicados.

### V12–V15 · Calidad del vocabulario y del respaldo
- **V13 — Vocabulario único.** Todo descriptor curado debe resolver a un término preferido del
  tesauro. Nació de encontrar dos vocabularios en paralelo.
- **V14 — Tesauro sin nombres de fuentes.** Ningún término del tesauro puede ser el nombre de una
  norma o de un órgano. *Citar una ley no dice de qué trata un texto* — para eso está la vía
  «norma», que además distingue el artículo.
- **V15 — Normas de la ficha respaldadas.** Toda norma declarada debe hallarse en el documento.

### C1–C7 · Consistencia entre vistas
Que cada cifra, rótulo y relación que la interfaz muestra salga del **índice único**, y que ninguna
vista se alimente de datos escritos a mano que quedaron desfasados.

Al correrse por primera vez, **5 de 7 estaban en rojo**.

---

## Prueba negativa: la suite debe poder fallar

Una suite que nunca falla es una suite en la que no se puede confiar. El verificador de citas se
somete a mutación deliberada:

| Prueba sobre MM 5939/2025 | Resultado |
|---|---|
| Cita literal correcta | ✓ PASA |
| Una palabra alterada («excede» → «supera») | ✕ FALLA |
| Cita inventada plausible | ✕ FALLA |
| Paráfrasis presentada como cita | ✕ FALLA |

Cambiar una sola palabra hace fallar la verificación. Esa es la garantía.

---

## Cómo se agregan reglas nuevas

El patrón que se repitió toda la construcción:

1. Aparece un defecto (lo ve alguien, o lo delata otra verificación).
2. Se busca la **causa raíz**, no el síntoma.
3. Se expresa como invariante: *«esto nunca debe pasar»*.
4. Se convierte en verificación, y se corre sobre todo el corpus.
5. **Casi siempre encuentra más casos** que el que motivó la regla.

V14 nació de un error señalado sobre un documento; al nacer encontró dos más que nadie había
mirado. Esa asimetría es la que hace escalable el método: **cada error hallado una vez se
convierte en una regla que lo impide para siempre.**
