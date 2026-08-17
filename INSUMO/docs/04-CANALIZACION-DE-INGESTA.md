# Canalización de ingesta

```
  01 Depósito     →  02 Texto      →  03 Segmentación →  04 Etiquetado
     sha256 del      congelado        pasajes por        tesauro con
     binario         por página       enumeración        peso de evidencia
                                      o párrafo
                                            ↓
  06 Publicación  ←  05b Revisión   ←  05a Integridad
     índice +          COMPUERTA         COMPUERTA
     alertas           abogado firma     22 verificaciones
```

**Las dos compuertas son bloqueantes.** Nada se publica sin cita verificada y sin firma humana.

## 01 · Depósito
El PDF llega a la carpeta o se carga por la aplicación. Se calcula `sha256` del binario y se
registra. Si el hash cambia después, las citas asociadas quedan marcadas para revalidación.

**Integración con CeroPapel:** 12 de los 20 documentos son impresiones de `ceropapel.conaf.cl`
con `idDocumento` estable en la URL. Es la vía natural de ingesta automática, y evita duplicar el
gestor documental.

## 02 · Texto congelado
Extracción por página con `pdftotext -layout` (poppler). OCR solo si no hay capa de texto — los 20
documentos actuales **no lo requirieron**. El resultado se guarda inmutable: es la base de toda
verificación posterior.

**Normalización canónica** antes de comparar: ligaduras tipográficas (`ﬁ`, `ﬂ`, `ﬀ`), comillas y
guiones tipográficos, espacios no separables, colapso de espacio en blanco.

*Detalle no obvio:* el guion al final de línea **se conserva**. En este corpus las 6 ocurrencias
son guiones con significado («jurídico-administrativo», «075-2020»), ninguna es corte silábico.
Borrarlo produciría «jurídicoadministrativo».

## 03 · Segmentación en pasajes
Dos estrategias, en cascada:

1. **Por enumeración** — ordinales (`PRIMERO:` … `DUODÉCIMO:`), numeradas (`1.`, `2)`), literales
   (`a)`), viñetas y secciones romanas.
2. **Por párrafo** — respaldo para documentos redactados en prosa continua. Sin esto quedarían con
   cero pasajes, es decir, **invisibles** (verificado por V05).

Cada pasaje se recorta al tramo que es **subcadena literal y contigua** del texto congelado
(V02) y se cierra en límite de oración.

El pasaje que contiene el criterio principal se marca; si la segmentación lo partió, se construye
uno anclado a la cita. **Ningún documento puede quedar sin criterio principal** (V04).

## 04 · Etiquetado
Tesauro con peso de evidencia (frase = 2, término = 1, umbral = 2), extracción de normas y
detección de referencias salientes con identidad canónica.

## 05a · Compuerta de integridad
22 verificaciones. Si una bloqueante falla, **el índice no se publica**. Ver
`03-REGLAS-DE-CALIDAD.md`.

## 05b · Compuerta de revisión
Un abogado confirma criterio, fuerza, alcance, naturaleza y relaciones. Solo ve lo que las
verificaciones no pueden decidir.

**Tamaño real de esta cola** sobre el corpus actual: de 230 etiquetas de materia asignadas, 149
(65%) tienen evidencia múltiple y son auto-aceptables; 81 (35%) descansan en una sola frase.
Agrupadas por documento+materia son **38 decisiones humanas**, no 285 párrafos.

## 06 · Publicación
Se indexa, se disparan las alertas de impacto normativo y de tensión, y se registra en la bitácora
inmutable.

---

## Estado del cierre de citas tras la ingesta actual

| Clase de referencia | Cantidad | Peso |
|---|---|---|
| doctrina externa | 12 | crítico |
| instrucción CONAF | 3 | alto |
| documento citado | 4 | medio |
| solicitud / trámite | 17 | bajo |

**Doctrina externa ausente (12):**

- Dictamen CGR E33624/2020 — invocado por 4 pronunciamiento(s). *CONAF se enmarca en el concepto de órganos y servicios públicos creados para el cumplimiento de la función administrativa.*
- Dictamen DT 1084/013 (2012) — invocado por 2 pronunciamiento(s). *Régimen del personal de CONAF: DL 249 con Código del Trabajo supletorio.*
- Dictamen CGR 12.528/1996 — invocado por 1 pronunciamiento(s). *Las tareas inherentes a la función pública no se encomiendan a terceros.*
- Dictamen CGR 443357/2024 — invocado por 1 pronunciamiento(s). *Exige al menos tres jornadas diarias presenciales dentro de la jornada semanal.*
- Dictamen CGR 9.527/2013 — invocado por 1 pronunciamiento(s). *Improcedente externalizar la función de inspección.*
- Dictamen CGR D263/2026 — invocado por 1 pronunciamiento(s). *Reconsidera la jurisprudencia sobre viviendas fiscales; 60 días hábiles para dictar normativa interna.*
- Dictamen CGR E125384/2021 — invocado por 1 pronunciamiento(s)
- Dictamen CGR E149544/2025 — invocado por 1 pronunciamiento(s). *Estricta sujeción a las bases, en la etapa licitatoria y en la ejecución del contrato.*
- Dictamen CGR E284318/2022 — invocado por 1 pronunciamiento(s)
- Dictamen DT 1949/032 (2021) — invocado por 1 pronunciamiento(s). *Aplicación de la Ley 21.220 de trabajo a distancia al personal de CONAF.*
- Dictamen E23562 — invocado por 1 pronunciamiento(s)
- Oficio CGR E69939/2025 — invocado por 1 pronunciamiento(s). *El art. 35 quáter es preventivo, amplio y objetivo; opera respecto de todo el organismo.*

Sin la clasificación, la lista de 36 vacíos es inmanejable. Con ella, la acción es evidente:
incorporar primero los 12 de doctrina externa, empezando por el E33624/2020.
