# Especificación funcional

## 1. Modelo conceptual

### La unidad recuperable es el pasaje, no el documento

Un memorándum dice cosas sobre materias distintas de la suya. El MM 4187/2026 tiene por materia
las fichas digitales, pero contiene reglas sobre geolocalización, Reglamento Interno, borrado
remoto y uso del teléfono propio. Indexando un criterio por documento, todo eso es irrecuperable.

Sobre el corpus actual: **20 documentos → 285 pasajes** (14,3× más unidades recuperables).

Cada pasaje se marca como **principal** (contiene el criterio central del documento) o
**incidental** (se dijo al pasar, a propósito de otra cosa). El abogado necesita saber cuál es cuál.

### Campos que evitan errores de interpretación

| Campo | Valores | Por qué existe |
|---|---|---|
| `jerarquia` | vinculante · instruccional · asesor · técnico | CGR y CPLT vinculan; Dirección Ejecutiva instruye; Fiscalía asesora. Un memo de Fiscalía de 2026 no desplaza un dictamen CGR de 2020. |
| `fuerza` | concluye · estima · recomienda · sugiere · hace_presente · consulta | El MM 3129/2022 concluye, sugiere y recomienda cosas distintas en un párrafo. Una sugerencia no debe citarse después como doctrina firme. |
| `alcance` | general · caso_concreto | Impide sobreextender una respuesta particular. |
| `naturaleza` | propio · citado · **desestimado** | El MM 5532/2020 transcribe la tesis de la Gerencia **para rechazarla**. Sin este campo, un índice ingenuo la devuelve como criterio de Fiscalía. |
| `estado` | vigente · vigencia_diferida · requiere_revision · consulta_pendiente · superado | Los OF 440 y 444/2026 son preguntas sin respuesta: no son doctrina y no deben citarse como tal. |

---

## 2. Búsqueda

### Cuatro vías independientes, más el cierre por citas

| Vía | Qué hace |
|---|---|
| **descriptor** | Materia curada por un abogado al ingresar el documento. |
| **texto** | Coincidencia en el pasaje, con lematización española. |
| **norma** | Norma invocada dentro del pasaje. |
| **tesauro** | Término preferido o sinónimo del vocabulario controlado. |
| **cita** | Cierre por grafo, **solo desde el conjunto directo**. |

El resultado declara por cuáles vías llegó cada documento (**convergencia N/5**). Un documento
alcanzado por una sola vía indica un hueco en su indexación, no menor relevancia: la interfaz lo
señala explícitamente y pide revisar su descriptor.

### Regla crítica: dos niveles de resultado

La consulta distingue si el término **nombra la materia** o es **específico dentro de ella**:

- `monumentos naturales` → nombra la materia → se devuelve completa.
- `teletrabajo` → término específico → los directos son los que lo tratan; el resto queda abajo,
  separado, bajo «Misma materia, sin mencionar el término».

**Por qué importa:** sin esta distinción, `teletrabajo` devolvía los 6 documentos de «Gestión de
personas» —incluido uno sobre Planes de Manejo que solo citaba el Estatuto Administrativo— y lo
ponía **primero** en la cronología por ser el más antiguo. Un resultado equivocado al inicio de
una cronología se lee como «lo primero que se dijo del tema».

### La ampliación exige descriptor curado

Para que un documento aparezca como «misma materia» no basta una frase detectada automáticamente:
la materia debe estar entre los **descriptores que un abogado le asignó**. La materia inferida por
tesauro sirve para encontrar pasajes dentro de un resultado directo, no para afirmar parentesco
entre documentos.

---

## 3. Las siete vistas

### 3.1 Consulta
Buscador libre + sugerencias. Resultados en dos bloques (directos / misma materia), cada uno en
orden cronológico ascendente. Por documento: criterio, cita literal verificada con página y
sha256, normas, relaciones, y los pasajes adicionales que coinciden.

Encabezado: número de documentos, rango de fechas, jerarquía máxima presente, convergencia,
documentos de una sola vía, y **aviso de alcance incompleto** cuando los resultados se apoyan en
autoridades externas ausentes del repositorio.

### 3.2 Líneas de criterio
Cadenas de evolución con el **verbo** que une cada eslabón: confirma · reitera · matiza · extiende ·
restringe · revierte · deja sin efecto · consolida · tensión con.

Los nodos en gris son documentos que el corpus cita y no contiene: la cadena se muestra
**incompleta** en vez de presentarse cerrada.

Cuatro cadenas activas: monumentos naturales, reforestación, protección de datos, planes de manejo.

### 3.3 Cierre de citas
El grafo de referencias salientes, con identidad canónica y clasificación:

| Clase | Peso |
|---|---|
| doctrina externa | Crítica — sostiene el criterio |
| instrucción CONAF | Alta — fija criterio propio |
| documento citado | Media |
| solicitud / trámite | Baja — es el memo que originó la consulta |

Sin esta clasificación la lista de vacíos es inmanejable: 17 de los 36 son solicitudes.

### 3.4 Corpus
Registro completo con ficha normalizada y profundidad del índice.

### 3.5 Normas
Índice inverso: norma → documentos. Responde «si esta ley cambia, ¿qué criterios quedan
expuestos?». Construido desde **fuente única** (ficha ∪ texto) con procedencia declarada.

### 3.6 Confiabilidad
Las 22 verificaciones con su resultado, la prueba negativa del verificador de citas, los defectos
que la suite encontró, alertas activas y calendario de vigencias.

### 3.7 Arquitectura
Canalización de ingesta, modelo de datos, API, componentes, plan por fases y límites de diseño.

---

## 4. Pendiente de construir

**Dossier exportable con certificado de alcance.** Es el entregable que el abogado adjunta al
informe: materia consultada, cronología con citas verificadas, mapa de concordancias y
divergencias, normativa con estado de vigencia, y vacíos declarados.

Encabezado por un **certificado de alcance**: qué se buscó, por qué vías, sobre cuántos
documentos, a qué nivel de cierre de citas, y qué quedó explícitamente fuera. Eso es lo que
permite firmar el informe con tranquilidad y explicar, si mañana aparece un documento nuevo, por
qué no estaba.
