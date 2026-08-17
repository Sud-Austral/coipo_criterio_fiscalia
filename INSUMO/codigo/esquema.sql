-- ═══════════════════════════════════════════════════════════════════════
-- Repositorio de Criterios · Fiscalía CONAF
-- Esquema PostgreSQL 16 — versión de referencia del prototipo
--
-- Principio rector: la regla de trazabilidad vive en la base de datos, no en
-- la aplicación, de modo que ninguna vía de escritura pueda saltársela.
-- ═══════════════════════════════════════════════════════════════════════

CREATE TYPE jerarquia_t  AS ENUM ('vinculante','instruccional','asesor','tecnico');
CREATE TYPE tipo_doc_t   AS ENUM ('memorandum','oficio','resolucion','dictamen','decision');
CREATE TYPE estado_t     AS ENUM ('vigente','vigencia_diferida','requiere_revision',
                                  'consulta_pendiente','superado');
CREATE TYPE fuerza_t     AS ENUM ('concluye','estima','recomienda','sugiere',
                                  'hace_presente','consulta');
CREATE TYPE alcance_t    AS ENUM ('general','caso_concreto');
CREATE TYPE naturaleza_t AS ENUM ('propio','citado','desestimado');

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

-- ═══ Vistas de consulta ═══════════════════════════════════════════════

-- Cronología por descriptor: la consulta central de la aplicación.
CREATE VIEW v_cronologia AS
SELECT d.fecha, d.slug, d.tipo, d.numero, d.anio, o.nombre AS organo,
       o.jerarquia, d.materia, c.sintesis, c.fuerza, c.alcance, c.naturaleza,
       ci.texto AS cita, ci.pagina, encode(d.sha256,'hex') AS sha256,
       d.archivo_uri, ds.descriptor_id
FROM   documento d
JOIN   organo o              ON o.id = d.organo_id
JOIN   criterio c            ON c.documento_id = d.id
LEFT   JOIN cita ci          ON ci.criterio_id = c.id
JOIN   documento_descriptor ds ON ds.documento_id = d.id
WHERE  c.naturaleza <> 'desestimado'       -- nunca devolver lo que el documento rechaza
ORDER  BY d.fecha;

-- Impacto normativo: qué criterios quedan expuestos cuando una norma se sustituye.
CREATE VIEW v_impacto_normativo AS
SELECT n.cuerpo, n.articulo, n.vigente_hasta,
       ns.cuerpo AS sustituida_por,
       count(DISTINCT d.id) AS documentos_afectados,
       array_agg(DISTINCT d.slug ORDER BY d.slug) AS pronunciamientos
FROM   norma n
LEFT   JOIN norma ns ON ns.id = n.sustituida_por
JOIN   criterio_norma cn ON cn.norma_id = n.id
JOIN   criterio c        ON c.id = cn.criterio_id
JOIN   documento d       ON d.id = c.documento_id
WHERE  n.vigente_hasta IS NOT NULL
GROUP  BY n.cuerpo, n.articulo, n.vigente_hasta, ns.cuerpo;

-- Vacíos: documentos citados por el corpus que no están incorporados.
CREATE VIEW v_vacios AS
SELECT r.destino_ext AS documento_referido,
       array_agg(DISTINCT d.slug ORDER BY d.slug) AS citado_en,
       count(*) AS menciones
FROM   relacion r
JOIN   criterio c  ON c.id = r.origen_id
JOIN   documento d ON d.id = c.documento_id
WHERE  r.destino_ext IS NOT NULL AND r.destino_id IS NULL
GROUP  BY r.destino_ext
ORDER  BY menciones DESC;
