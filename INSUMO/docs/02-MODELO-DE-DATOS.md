# Modelo de datos

## Principio

**Las reglas viven en la base, no en la aplicación**, de modo que ninguna vía de escritura pueda
saltárselas: ni la API, ni una carga masiva, ni la consola.

## Esquema PostgreSQL 16

```sql
-- ═══ Núcleo documental ═══════════════════════════════════════════════
CREATE TABLE organo (
  id            smallserial PRIMARY KEY,
  nombre        text NOT NULL UNIQUE,
  jerarquia     jerarquia_t NOT NULL      -- vinculante|instruccional|asesor|tecnico
);

CREATE TABLE documento (
  id            bigserial PRIMARY KEY,
  slug          text NOT NULL UNIQUE,     -- 'MM-4187-2026'
  tipo          tipo_doc_t NOT NULL,      -- memorandum|oficio|resolucion|dictamen|decision
  numero        text NOT NULL,
  anio          smallint NOT NULL,
  fecha         date NOT NULL,
  organo_id     smallint NOT NULL REFERENCES organo,
  firmante      text NOT NULL,
  destinatario  text,
  materia       text NOT NULL,
  estado        estado_t NOT NULL DEFAULT 'vigente',
  -- Trazabilidad del binario: si el PDF cambia, el hash cambia y las citas
  -- asociadas quedan marcadas para revalidación.
  archivo_uri   text NOT NULL,
  sha256        bytea NOT NULL,
  paginas       smallint NOT NULL,
  texto_plano   text NOT NULL,            -- extracción congelada, base de la verificación
  busqueda      tsvector GENERATED ALWAYS AS
                  (to_tsvector('spanish', coalesce(materia,'') || ' ' || coalesce(texto_plano,''))) STORED,
  creado_en     timestamptz NOT NULL DEFAULT now(),
  creado_por    text NOT NULL,
  UNIQUE (tipo, numero, anio)
);
CREATE INDEX ON documento USING gin (busqueda);
CREATE INDEX ON documento (fecha DESC);

-- ═══ Criterio: la unidad jurídica real, no el documento ═══════════════
-- Un documento puede contener más de un criterio, con distinta fuerza y alcance.
CREATE TABLE criterio (
  id            bigserial PRIMARY KEY,
  documento_id  bigint NOT NULL REFERENCES documento ON DELETE CASCADE,
  orden         smallint NOT NULL,
  sintesis      text NOT NULL,            -- paráfrasis, editable
  fuerza        fuerza_t NOT NULL,        -- concluye|estima|recomienda|sugiere|hace_presente|consulta
  alcance       alcance_t NOT NULL,       -- general|caso_concreto
  naturaleza    naturaleza_t NOT NULL     -- propio|citado|desestimado
                  DEFAULT 'propio',
  UNIQUE (documento_id, orden)
);

-- ═══ Cita literal — el ancla de trazabilidad ══════════════════════════
CREATE TABLE cita (
  id            bigserial PRIMARY KEY,
  criterio_id   bigint NOT NULL REFERENCES criterio ON DELETE CASCADE,
  texto         text NOT NULL,            -- verbatim del documento
  pagina        smallint,
  offset_inicio integer,                  -- posición en documento.texto_plano
  offset_fin    integer,
  verificada    boolean NOT NULL DEFAULT false,
  verificada_en timestamptz,
  sha_al_verif  bytea                     -- hash del PDF al momento de verificar
);
-- Regla dura: ninguna cita se publica sin verificar. Se aplica en trigger,
-- no en la aplicación, para que ninguna vía de escritura pueda saltársela.
CREATE OR REPLACE FUNCTION fn_cita_verificada() RETURNS trigger AS $$
BEGIN
  IF NEW.verificada IS NOT TRUE THEN
    RAISE EXCEPTION 'Cita % no verificada contra el texto fuente', NEW.id;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

-- ═══ Vocabulario controlado y normativa ═══════════════════════════════
CREATE TABLE descriptor (
  id       smallserial PRIMARY KEY,
  nombre   text NOT NULL UNIQUE,
  padre_id smallint REFERENCES descriptor    -- tesauro jerárquico
);
CREATE TABLE documento_descriptor (
  documento_id bigint  REFERENCES documento ON DELETE CASCADE,
  descriptor_id smallint REFERENCES descriptor,
  PRIMARY KEY (documento_id, descriptor_id)
);

CREATE TABLE norma (
  id            serial PRIMARY KEY,
  cuerpo        text NOT NULL,            -- 'Ley 19.886'
  articulo      text,                     -- '35 quáter'
  vigente_hasta date,                     -- se llena cuando la norma es sustituida
  sustituida_por integer REFERENCES norma,
  UNIQUE (cuerpo, articulo)
);
CREATE TABLE criterio_norma (
  criterio_id bigint REFERENCES criterio ON DELETE CASCADE,
  norma_id    integer REFERENCES norma,
  PRIMARY KEY (criterio_id, norma_id)
);

-- ═══ Relaciones entre criterios: el verbo es el dato ══════════════════
CREATE TYPE relacion_t AS ENUM
  ('confirma','reitera','matiza','extiende','restringe','revierte',
   'deja_sin_efecto','consolida','aplica','tension_con');

CREATE TABLE relacion (
  origen_id   bigint NOT NULL REFERENCES criterio ON DELETE CASCADE,
  destino_id  bigint REFERENCES criterio ON DELETE CASCADE,
  destino_ext text,                       -- documento citado aún no incorporado
  tipo        relacion_t NOT NULL,
  nota        text,
  CHECK (destino_id IS NOT NULL OR destino_ext IS NOT NULL)
);

-- ═══ Auditoría — inmutable ════════════════════════════════════════════
CREATE TABLE bitacora (
  id        bigserial PRIMARY KEY,
  tabla     text NOT NULL,
  registro  bigint NOT NULL,
  accion    text NOT NULL,
  antes     jsonb,
  despues   jsonb,
  usuario   text NOT NULL,
  en        timestamptz NOT NULL DEFAULT now()
);
REVOKE UPDATE, DELETE ON bitacora FROM PUBLIC;

CREATE TRIGGER tg_cita_verificada
  BEFORE INSERT OR UPDATE ON cita
  FOR EACH ROW EXECUTE FUNCTION fn_cita_verificada();
```

El DDL completo, con tipos enumerados y vistas de consulta, está en `codigo/esquema.sql`.

## Decisiones de diseño

### El criterio es la unidad jurídica, no el documento
Un memorándum puede contener varios criterios con distinta fuerza. El MM 3129/2022 **concluye**
sobre la procedencia, **sugiere** sobre el correo y **recomienda** sobre el teléfono: son tres
registros, no uno.

### La naturaleza distingue lo propio de lo rechazado
`naturaleza ∈ {propio, citado, desestimado}`. El MM 5532/2020 transcribe la tesis de la Gerencia
para rechazarla; marcada como `desestimado`, nunca puede devolverse como criterio de Fiscalía.

### El hash convierte el reemplazo silencioso en error visible
Si alguien sustituye el PDF, el `sha256` deja de coincidir y **todas las citas del documento pasan
a no verificadas** hasta revalidarse. Sin esto, una cita puede apuntar silenciosamente a otro texto.

### El texto congelado es la base de toda verificación
`documento.texto_plano` guarda la extracción inmutable. Todas las comprobaciones de cita y pasaje
se hacen contra ella, no contra el PDF.

### El verbo de relación es el dato
`relacion_t ∈ {confirma, reitera, matiza, extiende, restringe, revierte, deja_sin_efecto,
consolida, aplica, tension_con}`. Una cronología sin verbos es una pila; con verbos es una
trayectoria.

### Las referencias externas se modelan igual que las internas
`relacion.destino_ext` permite apuntar a un documento que el corpus cita y no contiene. Eso es lo
que hace calculable el **cierre de citas**.

## Índice único de normas

Había dos listas para lo mismo: la curada en la ficha y la extraída del texto. Se fusionan en una
sola con procedencia declarada:

| origen | significado |
|---|---|
| `ficha` | La afirmó un abogado; el extractor no la detectó |
| `texto` | La detectó el extractor, con página |
| `ambas` | Confirmada por los dos caminos |

Estado actual: **155 entradas**, 8 confirmadas por ambas vías.

## API

| Método | Ruta | Devuelve |
|---|---|---|
| `GET` | `/api/criterios?descriptor=&desde=&hasta=` | Cronología por concepto. Devuelve criterios ordenados por fecha con cita, página y hash. |
| `GET` | `/api/lineas/:id` | Cadena de criterio: nodos internos y externos con el verbo de relación. |
| `GET` | `/api/documentos/:slug` | Ficha completa con criterios, normas y relaciones. |
| `GET` | `/api/normas/:id/documentos` | Índice inverso. Qué criterios se apoyan en una norma. |
| `GET` | `/api/alertas` | Normas sustituidas, vigencias diferidas, tensiones y consultas abiertas. |
| `GET` | `/api/vacios` | Documentos citados por el corpus que no están incorporados. |
| `POST` | `/api/ingesta` | Carga un PDF: extrae, congela texto, calcula hash, propone ficha para revisión. |
| `POST` | `/api/citas/:id/verificar` | Revalida una cita contra el texto congelado. Idempotente. |
| `GET` | `/api/exportar/informe` | Armazón de informe con citas verificadas y vacíos declarados. |

## Componentes

| Capa | Tecnología | Notas |
|---|---|---|
| Base de datos | PostgreSQL 16 | tsvector con diccionario español para búsqueda literal; pg_trgm para aproximada; pgvector opcional para búsqueda semántica como capa secundaria, nunca como fuente de la cita. |
| API | Node + Fastify o Python + FastAPI | Sólo lectura para el 95% de los usos. La escritura pasa por revisión humana. |
| Front | React + TypeScript | TanStack Query para caché, TanStack Table para el corpus, Zod para validar los contratos de la API. |
| Extracción | pdftotext (poppler) + OCR opcional | Los 20 documentos actuales son PDF con capa de texto: no requirieron OCR. Se congela el texto extraído junto al hash del binario. |
| Verificación | Servicio propio | Normaliza ligaduras, comillas, guiones de corte y espacios; exige coincidencia exacta de subcadena. Corre en cada ingesta y en un job nocturno sobre todo el corpus. |
| Autenticación | SSO institucional CONAF | Roles: consulta (toda Fiscalía), edición (abogado responsable), publicación (Fiscal). |

### Nota sobre búsqueda semántica
Los *embeddings* pueden proponer «quizás esto también sea relevante», pero **la cita siempre
proviene del texto literal verificado**. Nunca deben ser la fuente de una cita: son una capa que
sugiere, no que afirma. Mantener esa frontera es lo que hace defendible el resultado.
