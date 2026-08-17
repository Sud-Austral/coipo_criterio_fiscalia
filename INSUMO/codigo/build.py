# -*- coding: utf-8 -*-
"""Genera el prototipo HTML autocontenido desde docs.json."""
import json, io, os

DOCS = json.load(open("/tmp/pron/app/docs.json", encoding="utf-8"))

# Cadenas de criterio curadas. Los nodos "externo" son documentos citados por el
# corpus pero que aún no están incorporados: el sistema los conoce y los marca.
LINEAS = [
  {
    "id": "monumentos",
    "titulo": "Monumentos naturales y el origen antrópico",
    "pregunta": "¿Alcanza la protección de Monumento Natural a los ejemplares plantados por acción humana?",
    "estado": "Criterio estable, extendido a nuevas especies",
    "nodos": [
      {"tipo": "externo", "fecha": "2011-04-18", "ref": "MM CONAF 1548/2011",
       "verbo": "origen", "texto": "Fija la doctrina institucional: la protección se diferencia cuando los individuos son producto de la intervención humana."},
      {"tipo": "doc", "id": "MM-5532-2020", "verbo": "desarrolla",
       "texto": "Belloto del Norte. Protección total e inviolabilidad dentro y fuera del bosque, pero sólo en medio natural y sin intervención humana."},
      {"tipo": "externo", "fecha": "2023-01-01", "ref": "Dictamen CGR E389863/2023",
       "verbo": "confirma", "vinculante": True,
       "texto": "La declaración no afecta a los individuos producto de la intervención humana. Corresponde a CONAF fijar el alcance de la protección."},
      {"tipo": "doc", "id": "MM-2698-2026", "verbo": "extiende",
       "texto": "Aplica el criterio a Araucaria araucana plantada, agregando la exigencia de Plan de Manejo de Plantaciones por estar el predio inserto en Parque Nacional."},
    ],
  },
  {
    "id": "reforestacion",
    "titulo": "Reforestación como medida de compensación ambiental",
    "pregunta": "¿Hasta cuándo son exigibles las obligaciones de reforestación de un PAS?",
    "estado": "Tensión no resuelta sobre el criterio de término",
    "nodos": [
      {"tipo": "externo", "fecha": "2021-12-21", "ref": "Oficio CONAF 747/2021",
       "verbo": "origen", "texto": "CONAF consulta a la SMA por el plazo de las obligaciones de reforestación de los PAS."},
      {"tipo": "externo", "fecha": "2022-05-02", "ref": "Oficio CONAF 212/2022",
       "verbo": "reitera", "texto": "Reitera la consulta a la SMA."},
      {"tipo": "externo", "fecha": "2022-07-01", "ref": "Ordinario SMA 1625/2022",
       "verbo": "responde", "vinculante": True,
       "texto": "La vida útil podría no ser variable idónea; lo relevante es que la obligación cumpla su fin ambiental."},
      {"tipo": "doc", "id": "MM-3400-2022", "verbo": "recoge",
       "texto": "Instruye exigir equivalencia del sitio, caracterización del ecosistema afectado y cronología con metas."},
      {"tipo": "doc", "id": "MM-3320-2026", "verbo": "matiza",
       "texto": "Afirma vigencia durante toda la vida útil del proyecto y fiscalización por ciclo de vida cuando la RCA no fija plazo expreso.",
       "tension": "Convive con el criterio de la SMA recogido en 2022. Ambos coinciden en que no hay liberación al tercer año; difieren en el criterio de término."},
    ],
  },
  {
    "id": "datos",
    "titulo": "Protección de datos personales",
    "pregunta": "¿Qué datos puede tratar y comunicar CONAF, y bajo qué estándar?",
    "estado": "Cambio de estatuto legal en curso — revisión obligada antes del 01-12-2026",
    "nodos": [
      {"tipo": "doc", "id": "MM-3129-2022", "verbo": "origen",
       "texto": "Bajo la Ley 19.628: entrega acotada a nombre y correo; se recomienda excluir el teléfono."},
      {"tipo": "doc", "id": "CPLT-C7949-21", "verbo": "delimita", "vinculante": True,
       "texto": "La Ley 19.628 no alcanza a las personas jurídicas; el tarjado de datos de personas naturales es correcto."},
      {"tipo": "externo", "fecha": "2024-12-13", "ref": "Ley 21.719",
       "verbo": "sustituye", "vinculante": True,
       "texto": "Sustituye íntegramente la Ley 19.628. Vigencia: 01-12-2026."},
      {"tipo": "doc", "id": "MM-4187-2026", "verbo": "reencuadra",
       "texto": "Primer pronunciamiento construido sobre el nuevo estatuto: base de licitud sin consentimiento, exclusión de datos sensibles, evaluación de impacto previa."},
    ],
  },
  {
    "id": "planes",
    "titulo": "Admisibilidad de solicitudes de Plan de Manejo",
    "pregunta": "¿Qué documentación legal se exige según la calidad que invoca el interesado?",
    "estado": "Criterio vigente — dos piezas de la cadena aún no incorporadas al repositorio",
    "nodos": [
      {"tipo": "externo", "fecha": "2023-08-05", "ref": "Oficio CONAF 464/2023",
       "verbo": "origen", "falta": True,
       "texto": "Primera instrucción sobre documentación exigible. Citado con dos fechas distintas dentro del MM 2665/2026."},
      {"tipo": "externo", "fecha": "2025-01-01", "ref": "Ley 21.770",
       "verbo": "modifica", "vinculante": True,
       "texto": "Ley Marco de Autorizaciones Sectoriales. Redefine 'interesado' en el art. 2 N°15 de la Ley 20.283."},
      {"tipo": "externo", "fecha": "2026-04-24", "ref": "Oficio CONAF 237/2026",
       "verbo": "homogeneiza", "falta": True,
       "texto": "Fija los criterios de admisibilidad según tipo de interesado. Es el acto que el MM 2665/2026 ratifica."},
      {"tipo": "doc", "id": "MM-2665-2026", "verbo": "ratifica",
       "texto": "Declara el Oficio 237 ajustado a derecho y plenamente vigente. Los literales del art. 22 se aplican de forma alternativa, no copulativa."},
    ],
  },
]

ALERTAS = [
  {"sev": "serious", "titulo": "Criterio apoyado en norma sustituida",
   "detalle": "MM 3129/2022 se funda íntegramente en la Ley 19.628, sustituida por la Ley 21.719 con vigencia 01-12-2026.",
   "accion": "Revisar y reemplazar antes del 01-12-2026.", "ref": "MM-3129-2022"},
  {"sev": "warning", "titulo": "Vigencia diferida",
   "detalle": "MM 4187/2026 razona sobre la Ley 21.719, que rige desde el 01-12-2026. El criterio es prospectivo por diseño.",
   "accion": "No citar como derecho vigente antes de esa fecha.", "ref": "MM-4187-2026"},
  {"sev": "warning", "titulo": "Tensión de criterio detectada",
   "detalle": "MM 3320/2026 y MM 3400/2022 difieren sobre si la vida útil del proyecto es la variable idónea para medir la vigencia de la obligación de reforestar.",
   "accion": "Requiere definición de la Gerencia. No hay acto que resuelva la divergencia.", "ref": "MM-3320-2026"},
  {"sev": "neutral", "titulo": "Consultas sin respuesta",
   "detalle": "OF 440/2026 (CGR, Ley 21.645) y OF 444/2026 (Comisión de Remuneraciones, Ley 20.300), ambos de 22-07-2026.",
   "accion": "No constituyen criterio. Bloqueados para cita como doctrina.",
   "ref": "OF-440-2026", "refs": ["OF-440-2026", "OF-444-2026"]},
]

VACIOS = [
  {"ref": "Oficio CONAF 464/2023", "citado_en": "MM 2665/2026", "materia": "Documentación exigible en Planes de Manejo"},
  {"ref": "Oficio CONAF 237/2026", "citado_en": "MM 2665/2026", "materia": "Criterios de admisibilidad por tipo de interesado"},
  {"ref": "MM CONAF 1548/2011", "citado_en": "MM 5532/2020 · MM 2698/2026", "materia": "Doctrina sobre Monumentos Naturales"},
  {"ref": "Oficio CONAF 521/2020", "citado_en": "MM 5939/2025", "materia": "Planos de subdivisión y superficie actual"},
  {"ref": "Oficio CONAF 747/2021 · 212/2022", "citado_en": "MM 3320/2026 · MM 3400/2022", "materia": "Consultas a la SMA sobre reforestación"},
  {"ref": "Informe Final Inv. Especial 555/2025", "citado_en": "MM 1688/2026", "materia": "Observación CGR sobre convenios"},
]

PRUEBA = [
  {"caso": "Cita literal correcta", "texto": "…no hay posibilidad de aplicar márgenes de tolerancia cuando una solicitud <b>excede</b> la superficie consignada en los títulos", "res": True},
  {"caso": "Una palabra alterada", "texto": "…no hay posibilidad de aplicar márgenes de tolerancia cuando una solicitud <b>supera</b> la superficie consignada en los títulos", "res": False},
  {"caso": "Cita inventada, plausible", "texto": "se acepta una tolerancia del 5% para predios mayores a 100 hectáreas", "res": False},
  {"caso": "Paráfrasis presentada como cita", "texto": "CONAF no puede aplicar tolerancias sobre la cabida de los títulos", "res": False},
]

CALENDARIO = [
  {"fecha": "2026-12-01", "hito": "Entra en vigencia la Ley 21.719 de protección de datos personales",
   "impacto": "2 pronunciamientos afectados · 1 requiere reemplazo"},
  {"fecha": "2027-04-01", "hito": "Consolidación metodológica de las acciones de control de perros asilvestrados 2026",
   "impacto": "OF 442/2026 — recién entonces hay resultados reportables"},
  {"fecha": "s/f", "hito": "Entrada en operación del Servicio Nacional Forestal (Ley 21.744)",
   "impacto": "4 pronunciamientos anticipan el cambio de estándar de juridicidad"},
]

ESQUEMA = """-- ═══ Núcleo documental ═══════════════════════════════════════════════
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
REVOKE UPDATE, DELETE ON bitacora FROM PUBLIC;"""

API = [
  ("GET",  "/api/criterios?descriptor=&desde=&hasta=", "Cronología por concepto. Devuelve criterios ordenados por fecha con cita, página y hash."),
  ("GET",  "/api/lineas/:id", "Cadena de criterio: nodos internos y externos con el verbo de relación."),
  ("GET",  "/api/documentos/:slug", "Ficha completa con criterios, normas y relaciones."),
  ("GET",  "/api/normas/:id/documentos", "Índice inverso. Qué criterios se apoyan en una norma."),
  ("GET",  "/api/alertas", "Normas sustituidas, vigencias diferidas, tensiones y consultas abiertas."),
  ("GET",  "/api/vacios", "Documentos citados por el corpus que no están incorporados."),
  ("POST", "/api/ingesta", "Carga un PDF: extrae, congela texto, calcula hash, propone ficha para revisión."),
  ("POST", "/api/citas/:id/verificar", "Revalida una cita contra el texto congelado. Idempotente."),
  ("GET",  "/api/exportar/informe", "Armazón de informe con citas verificadas y vacíos declarados."),
]

STACK = [
  ("Base de datos", "PostgreSQL 16", "tsvector con diccionario español para búsqueda literal; pg_trgm para aproximada; pgvector opcional para búsqueda semántica como capa secundaria, nunca como fuente de la cita."),
  ("API", "Node + Fastify o Python + FastAPI", "Sólo lectura para el 95% de los usos. La escritura pasa por revisión humana."),
  ("Front", "React + TypeScript", "TanStack Query para caché, TanStack Table para el corpus, Zod para validar los contratos de la API."),
  ("Extracción", "pdftotext (poppler) + OCR opcional", "Los 20 documentos actuales son PDF con capa de texto: no requirieron OCR. Se congela el texto extraído junto al hash del binario."),
  ("Verificación", "Servicio propio", "Normaliza ligaduras, comillas, guiones de corte y espacios; exige coincidencia exacta de subcadena. Corre en cada ingesta y en un job nocturno sobre todo el corpus."),
  ("Autenticación", "SSO institucional CONAF", "Roles: consulta (toda Fiscalía), edición (abogado responsable), publicación (Fiscal)."),
]

FASES = [
  ("Fase 1", "Repositorio verificable", "Ingesta, ficha estructurada, verificación de citas, búsqueda por descriptor y cronología. Es lo que muestra este prototipo.", "6–8 semanas"),
  ("Fase 2", "Trazabilidad normativa", "Índice inverso por norma, alertas de sustitución, calendario de vigencias, registro de consultas pendientes y detección de vacíos.", "4 semanas"),
  ("Fase 3", "Líneas de criterio", "Grafo de relaciones con verbo, detección asistida de tensión al ingresar un documento, vista de evolución.", "6 semanas"),
  ("Fase 4", "Armazón de informe", "Exportación a Word con la cronología, citas verificadas y vacíos declarados. Nunca redacta la conclusión.", "3 semanas"),
]

ESTADO_META = {
  "vigente":            ("good",    "Vigente"),
  "vigencia_diferida":  ("warning", "Vigencia diferida"),
  "requiere_revision":  ("serious", "Requiere revisión"),
  "consulta_pendiente": ("neutral", "Consulta pendiente"),
}
JERARQUIA_META = {
  "vinculante":    (1, "Vinculante"),
  "instruccional": (2, "Instruccional"),
  "asesor":        (3, "Asesor"),
  "tecnico":       (4, "Técnico"),
}
FUERZA_META = {
  "concluye": "concluye", "estima": "estima", "recomienda": "recomienda",
  "sugiere": "sugiere", "hace_presente": "hace presente", "consulta": "consulta (sin respuesta)",
}

payload = {
  "docs": DOCS, "lineas": LINEAS, "alertas": ALERTAS, "vacios": VACIOS,
  "prueba": PRUEBA, "calendario": CALENDARIO, "api": API, "stack": STACK,
  "fases": FASES, "estadoMeta": ESTADO_META, "jerarquiaMeta": JERARQUIA_META,
  "fuerzaMeta": FUERZA_META, "esquema": ESQUEMA,
}

HTML = r"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Repositorio de Criterios — Fiscalía CONAF · Prototipo</title>
<style>
:root{
  color-scheme:light;
  --paper:#faf9f6; --surface:#ffffff; --surface-2:#f5f4f0;
  --ink:#14140f; --ink-2:#54534d; --ink-3:#8a887f;
  --rule:#e3e1d9; --rule-2:#d3d0c6;
  --accent:#1d5c3f; --accent-2:#0f3d28; --accent-soft:#eef4f0;
  --good:#0ca30c; --good-ink:#00630 0; --good-ink:#006300;
  --warn:#fab219; --warn-ink:#7d5800;
  --serious:#ec835a; --serious-ink:#9c4318;
  --critical:#d03b3b; --critical-ink:#9c1f1f;
  --series-1:#2a78d6;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",sans-serif;
  --serif:Georgia,"Iowan Old Style","Times New Roman",serif;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-underline-offset:2px}
h1,h2,h3,h4{margin:0;font-weight:600;letter-spacing:-.011em}

/* ── Cabecera ─────────────────────────────────────────── */
.top{background:var(--surface);border-bottom:1px solid var(--rule)}
.top-in{max-width:1180px;margin:0 auto;padding:18px 28px 0}
.brandrow{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;flex-wrap:wrap}
.brand{display:flex;gap:13px;align-items:center}
.mark{width:34px;height:34px;border-radius:7px;background:var(--accent);color:#fff;
  display:grid;place-items:center;font-weight:700;font-size:13px;letter-spacing:.02em;flex:none}
.brand h1{font-size:16.5px}
.brand p{margin:1px 0 0;font-size:12.5px;color:var(--ink-3)}
.protobadge{font-size:11px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;
  color:var(--warn-ink);background:#fdf3dd;border:1px solid #f3e0ae;
  padding:4px 9px;border-radius:5px;align-self:center}
nav{display:flex;gap:2px;margin-top:16px;flex-wrap:wrap}
nav button{appearance:none;background:none;border:0;border-bottom:2px solid transparent;
  font:inherit;font-size:13.5px;color:var(--ink-2);padding:9px 13px;cursor:pointer;
  border-radius:5px 5px 0 0}
nav button:hover{background:var(--surface-2);color:var(--ink)}
nav button[aria-selected=true]{color:var(--accent-2);border-bottom-color:var(--accent);font-weight:600}

main{max-width:1180px;margin:0 auto;padding:26px 28px 80px}
.view{display:none}.view.on{display:block}

/* ── Piezas ───────────────────────────────────────────── */
.card{background:var(--surface);border:1px solid var(--rule);border-radius:9px}
.pad{padding:20px 22px}
.vh{font-size:19px;margin-bottom:5px}
.vsub{color:var(--ink-2);font-size:13.5px;max-width:76ch;margin:0 0 20px}
.sect{margin-top:34px}
.sect>h3{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);
  margin-bottom:11px;font-weight:650}

.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:11px;margin-bottom:24px}
.tile{background:var(--surface);border:1px solid var(--rule);border-radius:9px;padding:14px 16px}
.tile .lab{font-size:11.5px;color:var(--ink-3);letter-spacing:.02em;margin-bottom:5px}
.tile .val{font-size:27px;font-weight:600;line-height:1.05;letter-spacing:-.02em}
.tile .foot{font-size:11.5px;color:var(--ink-2);margin-top:4px}

.badge{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;
  padding:2.5px 8px;border-radius:20px;border:1px solid var(--rule-2);
  background:var(--surface-2);color:var(--ink-2);white-space:nowrap;letter-spacing:.01em}
.dot{width:7px;height:7px;border-radius:50%;flex:none}
.st-good .dot{background:var(--good)} .st-good{color:var(--good-ink);border-color:#bfe4bf;background:#f0f8f0}
.st-warning .dot{background:var(--warn)} .st-warning{color:var(--warn-ink);border-color:#f0dfae;background:#fdf6e6}
.st-serious .dot{background:var(--serious)} .st-serious{color:var(--serious-ink);border-color:#f3ceba;background:#fdf1eb}
.st-critical .dot{background:var(--critical)} .st-critical{color:var(--critical-ink);border-color:#eec4c4;background:#fcf0f0}
.st-neutral .dot{background:var(--ink-3)}
.jer{font-family:var(--mono);font-size:10.5px;letter-spacing:.04em;text-transform:uppercase;
  color:var(--ink-2);border:1px solid var(--rule-2);padding:2px 7px;border-radius:4px;background:var(--surface-2)}
.jer.j1{border-color:var(--accent);color:var(--accent-2);background:var(--accent-soft);font-weight:700}

/* ── Consulta ─────────────────────────────────────────── */
.chips{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:6px}
.chip{appearance:none;font:inherit;font-size:12.5px;background:var(--surface);
  border:1px solid var(--rule-2);color:var(--ink-2);padding:5px 12px;border-radius:20px;cursor:pointer}
.chip:hover{border-color:var(--accent);color:var(--accent-2)}
.chip[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
.chip .n{opacity:.6;margin-left:5px;font-variant-numeric:tabular-nums}
.chip[aria-pressed=true] .n{opacity:.75}

.resumen{border-left:3px solid var(--accent);background:var(--accent-soft);
  padding:13px 16px;border-radius:0 7px 7px 0;margin:18px 0 20px;font-size:13.5px;color:var(--ink-2)}
.resumen b{color:var(--ink)}

.tl{position:relative;padding-left:26px}
.tl::before{content:"";position:absolute;left:6px;top:8px;bottom:8px;width:1.5px;background:var(--rule-2)}
.node{position:relative;margin-bottom:14px}
.node::before{content:"";position:absolute;left:-24px;top:15px;width:11px;height:11px;
  border-radius:50%;background:var(--surface);border:2.5px solid var(--accent)}
.node.ext::before{border-color:var(--rule-2);background:var(--surface-2)}
.node.falta::before{border-color:var(--serious);border-style:dashed}

.doc{background:var(--surface);border:1px solid var(--rule);border-radius:9px;overflow:hidden}
.doc-h{padding:13px 17px;display:flex;gap:11px;align-items:baseline;flex-wrap:wrap;
  border-bottom:1px solid var(--rule);background:linear-gradient(var(--surface),var(--surface-2))}
.doc-id{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--accent-2)}
.doc-f{font-variant-numeric:tabular-nums;font-size:12.5px;color:var(--ink-2)}
.doc-t{flex:1 1 260px;font-size:14px;font-weight:600;min-width:200px}
.doc-b{padding:15px 17px}
.meta{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:11px;align-items:center}
.crit{font-size:14px;margin:0 0 13px}
.fuerza{font-style:italic;color:var(--ink-2)}

blockquote{margin:0 0 12px;padding:12px 15px;background:var(--surface-2);
  border-left:3px solid var(--rule-2);border-radius:0 6px 6px 0;
  font-family:var(--serif);font-size:14.5px;line-height:1.5;color:var(--ink)}
.qsrc{display:flex;gap:9px;flex-wrap:wrap;align-items:center;
  font-family:var(--mono);font-size:11px;color:var(--ink-3);margin-top:9px}
.qsrc .ok{color:var(--good-ink);font-weight:600}
.ruta{font-family:var(--mono);font-size:11px;color:var(--ink-3);word-break:break-all;
  padding-top:9px;border-top:1px dashed var(--rule);margin-top:11px}
.norms{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}
.norm{font-family:var(--mono);font-size:10.5px;color:var(--ink-2);background:var(--surface-2);
  border:1px solid var(--rule);padding:2px 7px;border-radius:4px}
.rel{font-size:12.5px;color:var(--ink-2);margin-top:9px;padding-left:13px;border-left:2px solid var(--rule-2)}
.rel b{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--accent-2)}
.warnbox{margin-top:11px;padding:10px 13px;border-radius:6px;font-size:12.5px;
  background:#fdf6e6;border:1px solid #f0dfae;color:var(--warn-ink)}
.warnbox.s{background:#fdf1eb;border-color:#f3ceba;color:var(--serious-ink)}
.desest{margin-top:11px;padding:10px 13px;border-radius:6px;font-size:12.5px;
  background:var(--surface-2);border:1px dashed var(--rule-2);color:var(--ink-2)}

/* ── Tablas ───────────────────────────────────────────── */
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);
  font-weight:650;padding:9px 11px;border-bottom:1.5px solid var(--rule-2);white-space:nowrap}
td{padding:10px 11px;border-bottom:1px solid var(--rule);vertical-align:top}
tbody tr:hover{background:var(--surface-2)}
td.m{font-family:var(--mono);font-size:11.5px;white-space:nowrap}
td.num{font-variant-numeric:tabular-nums;text-align:right}
.scroll{overflow-x:auto}

/* ── Gráfico ──────────────────────────────────────────── */
.chart{display:flex;align-items:flex-end;gap:12px;height:120px;padding:0 4px;margin-top:6px}
.bar-w{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;height:100%;justify-content:flex-end}
.bar{width:100%;max-width:52px;background:var(--series-1);border-radius:4px 4px 0 0;min-height:3px}
.bar-n{font-size:12px;font-weight:600;font-variant-numeric:tabular-nums}
.bar-x{font-size:11.5px;color:var(--ink-3);font-variant-numeric:tabular-nums;
  padding-top:6px;border-top:1px solid var(--rule-2);width:100%;text-align:center}

/* ── Anexo técnico ────────────────────────────────────── */
pre{background:#12140f;color:#e8e6dc;border-radius:9px;padding:18px 20px;overflow-x:auto;
  font-family:var(--mono);font-size:11.5px;line-height:1.62;margin:0}
pre .c{color:#7f9c72} pre .k{color:#9ec8f0} pre .t{color:#e6c07b} pre .s{color:#c8a2c8}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:13px}
.meth{border:1px solid var(--rule);border-radius:9px;padding:15px 17px;background:var(--surface)}
.meth h4{font-size:13.5px;margin-bottom:5px}
.meth p{margin:0;font-size:12.5px;color:var(--ink-2)}
.verb{display:inline-block;font-family:var(--mono);font-size:10px;font-weight:700;
  text-transform:uppercase;letter-spacing:.05em;padding:2px 7px;border-radius:4px;
  background:var(--accent-soft);color:var(--accent-2);border:1px solid #cfe0d6;margin-bottom:7px}
.verb.t{background:#fdf1eb;color:var(--serious-ink);border-color:#f3ceba}
.flow{display:flex;gap:9px;flex-wrap:wrap;align-items:stretch;margin-top:6px}
.step{flex:1 1 152px;border:1px solid var(--rule);border-radius:8px;padding:12px 13px;background:var(--surface)}
.step .n{font-family:var(--mono);font-size:10.5px;color:var(--accent);font-weight:700;letter-spacing:.05em}
.step h5{margin:4px 0 4px;font-size:12.5px;font-weight:600}
.step p{margin:0;font-size:11.5px;color:var(--ink-2);line-height:1.45}
.gate{border-color:var(--accent);background:var(--accent-soft)}
.foot{margin-top:44px;padding-top:18px;border-top:1px solid var(--rule);
  font-size:12px;color:var(--ink-3);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.chk{color:var(--good-ink);font-weight:700}
.xmk{color:var(--critical-ink);font-weight:700}
@media (max-width:640px){
  .top-in,main{padding-left:16px;padding-right:16px}
  .doc-h{gap:7px}
}
</style></head><body>

<header class="top"><div class="top-in">
  <div class="brandrow">
    <div class="brand">
      <div class="mark">FC</div>
      <div><h1>Repositorio de Criterios · Fiscalía</h1>
      <p>Corporación Nacional Forestal — aplicación interna</p></div>
    </div>
    <span class="protobadge">Prototipo · datos reales · 20 documentos</span>
  </div>
  <nav id="nav"></nav>
</div></header>

<main>
  <section class="view on" id="v-consulta"></section>
  <section class="view" id="v-lineas"></section>
  <section class="view" id="v-corpus"></section>
  <section class="view" id="v-normas"></section>
  <section class="view" id="v-control"></section>
  <section class="view" id="v-arq"></section>
</main>

<script>
const D = __PAYLOAD__;
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const byId = Object.fromEntries(D.docs.map(d => [d.id, d]));
const fFecha = f => { const [a,m,d] = f.split('-');
  const M = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
  return `${d} ${M[+m-1]} ${a}`; };
const rotulo = d => d.tipo === 'Decisión de amparo' ? `Amparo ${d.numero}`
  : `${d.tipo === 'Memorándum' ? 'MM.' : d.tipo === 'Oficio' ? 'OF.' :
      d.tipo === 'Resolución' ? 'Res.' : 'Dict.'} ${d.numero}/${d.anio}`;

function estadoBadge(e){ const [k,l] = D.estadoMeta[e];
  return `<span class="badge st-${k}"><span class="dot"></span>${l}</span>`; }
function jerBadge(j){ const [r,l] = D.jerarquiaMeta[j];
  return `<span class="jer j${r}" title="Jerarquía ${r} de 4">${l}</span>`; }

/* ══ Ficha de documento ══════════════════════════════════ */
function fichaHTML(d, {compacta=false} = {}){
  const rels = (d.relaciones||[]).map(r =>
    `<div class="rel"><b>${esc(r.tipo.replace(/_/g,' '))}</b> · ${esc(r.ref)}${
      r.nota ? ` — ${esc(r.nota)}` : ''}</div>`).join('');
  return `<article class="doc">
    <div class="doc-h">
      <span class="doc-id">${esc(rotulo(d))}</span>
      <span class="doc-f">${fFecha(d.fecha)}</span>
      <span class="doc-t">${esc(d.materia)}</span>
    </div>
    <div class="doc-b">
      <div class="meta">
        ${jerBadge(d.jerarquia)} ${estadoBadge(d.estado)}
        <span class="badge">${esc(d.organo)}</span>
        <span class="badge">${d.alcance === 'general' ? 'Criterio general' : 'Caso concreto'}</span>
      </div>
      <p class="crit"><span class="fuerza">${esc(d.firmante.split(',')[0])} ${
        esc(D.fuerzaMeta[d.fuerza])}:</span> ${esc(d.criterio)}</p>
      <blockquote>«${esc(d.cita)}»</blockquote>
      <div class="qsrc">
        <span class="ok">✓ cita verificada</span>
        <span>· pág. ${d.pagina}/${d.paginas}</span>
        <span>· sha256 ${esc(d.sha)}</span>
      </div>
      ${d.alerta ? `<div class="warnbox${d.estado==='requiere_revision'?' s':''}">⚠ ${esc(d.alerta)}</div>` : ''}
      ${d.desestima ? `<div class="desest"><b>Posición desestimada en el propio documento:</b> ${esc(d.desestima)}</div>` : ''}
      ${compacta ? '' : `<div class="norms">${d.normas.map(n =>
        `<span class="norm">${esc(n)}</span>`).join('')}</div>${rels}
      <div class="ruta">📎 ${esc(d.ruta)}</div>`}
    </div></article>`;
}

/* ══ 1 · Consulta por concepto ═══════════════════════════ */
const conteo = {};
D.docs.forEach(d => d.descriptores.forEach(t => conteo[t] = (conteo[t]||0)+1));
const tags = Object.keys(conteo).sort((a,b) => conteo[b]-conteo[a] || a.localeCompare(b,'es'));
let sel = 'Protección de datos personales';

function renderConsulta(){
  const hits = D.docs.filter(d => d.descriptores.includes(sel));
  const jerMin = Math.min(...hits.map(h => D.jerarquiaMeta[h.jerarquia][0]));
  const pend = hits.filter(h => h.estado === 'consulta_pendiente').length;
  const rev  = hits.filter(h => h.estado === 'requiere_revision').length;
  document.getElementById('v-consulta').innerHTML = `
    <h2 class="vh">¿Qué se ha dicho sobre…?</h2>
    <p class="vsub">Selecciona un descriptor del vocabulario controlado. El resultado es la cronología
    completa de lo pronunciado, de lo más antiguo a lo más reciente, con la cita literal, la página
    exacta y el hash del archivo de origen.</p>
    <div class="chips">${tags.map(t =>
      `<button class="chip" aria-pressed="${t===sel}" data-t="${esc(t)}">${esc(t)}<span class="n">${conteo[t]}</span></button>`
    ).join('')}</div>
    <div class="resumen">
      <b>${hits.length}</b> ${hits.length===1?'pronunciamiento':'pronunciamientos'} ·
      de <b>${fFecha(hits[0].fecha)}</b> a <b>${fFecha(hits[hits.length-1].fecha)}</b> ·
      jerarquía máxima presente: <b>${D.jerarquiaMeta[Object.entries(D.jerarquiaMeta)
        .find(([,v]) => v[0]===jerMin)[0]][1].toLowerCase()}</b>
      ${rev ? ` · <b style="color:var(--serious-ink)">${rev} requiere revisión</b>` : ''}
      ${pend ? ` · <b style="color:var(--ink-2)">${pend} consulta abierta que no constituye criterio</b>` : ''}
    </div>
    <div class="tl">${hits.map(d => `<div class="node">${fichaHTML(d)}</div>`).join('')}</div>`;
  document.querySelectorAll('#v-consulta .chip').forEach(b =>
    b.onclick = () => { sel = b.dataset.t; renderConsulta(); });
}

/* ══ 2 · Líneas de criterio ══════════════════════════════ */
function renderLineas(){
  document.getElementById('v-lineas').innerHTML = `
    <h2 class="vh">Líneas de criterio</h2>
    <p class="vsub">La cronología suelta no basta: lo que importa es cómo evolucionó el criterio.
    Cada eslabón declara el verbo que lo une al anterior — confirma, matiza, extiende, restringe,
    revierte. Los nodos en gris son documentos citados por el corpus que aún no están incorporados.</p>
    ${D.lineas.map(L => `
      <div class="sect">
        <div class="card pad" style="margin-bottom:16px">
          <h3 style="font-size:16px;margin-bottom:6px">${esc(L.titulo)}</h3>
          <p style="margin:0 0 9px;font-size:13.5px;color:var(--ink-2)">${esc(L.pregunta)}</p>
          <span class="badge ${L.estado.includes('Tensión') ? 'st-warning' :
            L.estado.includes('revisión') || L.estado.includes('obligada') ? 'st-serious' : 'st-good'}">
            <span class="dot"></span>${esc(L.estado)}</span>
        </div>
        <div class="tl">${L.nodos.map(n => {
          if (n.tipo === 'doc'){ const d = byId[n.id];
            return `<div class="node">
              <span class="verb${n.tension?' t':''}">${esc(n.verbo)}</span>
              ${fichaHTML(d, {compacta:true})}
              ${n.tension ? `<div class="warnbox" style="margin-left:0">⚠ <b>Tensión:</b> ${esc(n.tension)}</div>` : ''}
            </div>`; }
          return `<div class="node ext${n.falta?' falta':''}">
            <span class="verb">${esc(n.verbo)}</span>
            <div class="card pad" style="padding:13px 16px">
              <div style="display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;margin-bottom:6px">
                <span class="doc-id" style="color:var(--ink-2)">${esc(n.ref)}</span>
                <span class="doc-f">${n.fecha.endsWith('-01-01') ? n.fecha.slice(0,4) : fFecha(n.fecha)}</span>
                ${n.vinculante ? '<span class="jer j1">Vinculante</span>' : ''}
                ${n.falta ? '<span class="badge st-serious"><span class="dot"></span>No incorporado</span>'
                          : '<span class="badge">Referencia externa</span>'}
              </div>
              <p style="margin:0;font-size:13px;color:var(--ink-2)">${esc(n.texto)}</p>
            </div></div>`;
        }).join('')}</div>
      </div>`).join('')}`;
}

/* ══ 3 · Corpus ══════════════════════════════════════════ */
function renderCorpus(){
  const porAnio = {};
  D.docs.forEach(d => porAnio[d.anio] = (porAnio[d.anio]||0)+1);
  const anios = Object.keys(porAnio).sort();
  const max = Math.max(...Object.values(porAnio));
  document.getElementById('v-corpus').innerHTML = `
    <h2 class="vh">Corpus</h2>
    <p class="vsub">Registro completo. Cada fila es un documento con su ficha normalizada:
    jerarquía del órgano, fuerza del criterio, alcance, estado y ancla de trazabilidad.</p>
    <div class="grid2" style="margin-bottom:24px">
      <div class="card pad">
        <h3 style="font-size:13.5px;margin-bottom:2px">Documentos incorporados por año</h3>
        <p style="margin:0 0 4px;font-size:12px;color:var(--ink-3)">El corpus crece; el índice se actualiza por ingesta incremental.</p>
        <div class="chart">${anios.map(a => `
          <div class="bar-w">
            <span class="bar-n">${porAnio[a]}</span>
            <div class="bar" style="height:${Math.round(porAnio[a]/max*82)}%"></div>
            <span class="bar-x">${a}</span>
          </div>`).join('')}</div>
      </div>
      <div class="card pad">
        <h3 style="font-size:13.5px;margin-bottom:9px">Composición</h3>
        <table><tbody>
          ${Object.entries(D.jerarquiaMeta).map(([k,v]) => {
            const n = D.docs.filter(d => d.jerarquia===k).length;
            return `<tr><td>${jerBadge(k)}</td>
              <td style="font-size:12.5px;color:var(--ink-2)">${
                k==='vinculante'?'CGR y Consejo para la Transparencia':
                k==='instruccional'?'Dirección Ejecutiva':
                k==='asesor'?'Fiscalía':'Gerencia de Fiscalización'}</td>
              <td class="num" style="font-weight:600">${n}</td></tr>`;
          }).join('')}
        </tbody></table>
      </div>
    </div>
    <div class="card scroll"><table>
      <thead><tr><th>Documento</th><th>Fecha</th><th>Órgano</th><th>Materia</th>
        <th>Jerarquía</th><th>Fuerza</th><th>Alcance</th><th>Estado</th><th>Cita</th></tr></thead>
      <tbody>${D.docs.map(d => `<tr>
        <td class="m" style="color:var(--accent-2);font-weight:600">${esc(rotulo(d))}</td>
        <td class="m">${d.fecha}</td>
        <td style="font-size:12.5px">${esc(d.organo.replace('CONAF — ',''))}</td>
        <td style="max-width:290px">${esc(d.materia)}</td>
        <td>${jerBadge(d.jerarquia)}</td>
        <td style="font-size:12.5px;font-style:italic;color:var(--ink-2)">${esc(D.fuerzaMeta[d.fuerza])}</td>
        <td style="font-size:12.5px">${d.alcance==='general'?'General':'Caso'}</td>
        <td>${estadoBadge(d.estado)}</td>
        <td class="m"><span class="chk">✓</span> p.${d.pagina}</td></tr>`).join('')}</tbody>
    </table></div>`;
}

/* ══ 4 · Índice inverso por norma ════════════════════════ */
function renderNormas(){
  const idx = {};
  D.docs.forEach(d => d.normas.forEach(n => (idx[n] = idx[n]||[]).push(d)));
  const cuerpo = n => n.replace(/\s+art\..*$/,'');
  const grupos = {};
  Object.entries(idx).forEach(([n,ds]) => {
    const c = cuerpo(n);
    grupos[c] = grupos[c] || {arts:[], docs:new Set()};
    grupos[c].arts.push(n); ds.forEach(d => grupos[c].docs.add(d.id));
  });
  const orden = Object.keys(grupos).sort((a,b) =>
    grupos[b].docs.size - grupos[a].docs.size || a.localeCompare(b,'es'));
  document.getElementById('v-normas').innerHTML = `
    <h2 class="vh">Índice inverso por norma</h2>
    <p class="vsub">La pregunta que evita el error más caro: cuando una ley cambia,
    ¿qué pronunciamientos nuestros quedan expuestos? Este índice lo responde en un paso.</p>
    <div class="warnbox s" style="margin-bottom:22px;font-size:13.5px">
      <b>⚠ Impacto normativo detectado.</b> La <b>Ley 19.628</b> sostiene 2 pronunciamientos del corpus
      y será sustituida por la <b>Ley 21.719</b> el <b>1 de diciembre de 2026</b>.
      MM 3129/2022 se funda íntegramente en ella y requiere reemplazo antes de esa fecha.
    </div>
    <div class="card scroll"><table>
      <thead><tr><th>Cuerpo normativo</th><th>Disposiciones invocadas</th>
        <th class="num">Docs.</th><th>Pronunciamientos</th></tr></thead>
      <tbody>${orden.map(c => {
        const g = grupos[c], ds = [...g.docs].map(i => byId[i]).sort((a,b)=>a.fecha<b.fecha?-1:1);
        const alerta = c === 'Ley 19.628';
        return `<tr${alerta?' style="background:#fdf1eb"':''}>
          <td class="m" style="font-weight:600;color:${alerta?'var(--serious-ink)':'var(--accent-2)'}">
            ${esc(c)}${alerta?' ⚠':''}</td>
          <td style="font-size:12px;color:var(--ink-2)">${g.arts.map(a =>
            esc(a.replace(c,'').trim() || '—')).join(' · ')}</td>
          <td class="num" style="font-weight:600">${g.docs.size}</td>
          <td class="m">${ds.map(d =>
            `<span style="color:var(--accent-2)">${esc(rotulo(d))}</span>`).join(' · ')}</td>
        </tr>`;
      }).join('')}</tbody>
    </table></div>
    <p style="font-size:12px;color:var(--ink-3);margin-top:11px">
      ${orden.length} cuerpos normativos · ${Object.keys(idx).length} disposiciones distintas
      invocadas en 20 documentos.</p>`;
}

/* ══ 5 · Control ═════════════════════════════════════════ */
function renderControl(){
  document.getElementById('v-control').innerHTML = `
    <h2 class="vh">Control</h2>
    <p class="vsub">El panel que hace confiable a todo lo demás: verificación de citas,
    alertas activas, vacíos del corpus y calendario de vigencias.</p>

    <div class="tiles">
      <div class="tile"><div class="lab">Documentos</div><div class="val">20</div>
        <div class="foot">5 órganos emisores</div></div>
      <div class="tile"><div class="lab">Citas verificadas</div>
        <div class="val" style="color:var(--good-ink)">20/20</div>
        <div class="foot">coincidencia exacta</div></div>
      <div class="tile"><div class="lab">Alertas activas</div>
        <div class="val" style="color:var(--serious-ink)">4</div>
        <div class="foot">1 requiere acción con fecha</div></div>
      <div class="tile"><div class="lab">Consultas abiertas</div><div class="val">2</div>
        <div class="foot">CGR · Comisión Remuneraciones</div></div>
      <div class="tile"><div class="lab">Vacíos detectados</div><div class="val">6</div>
        <div class="foot">citados, no incorporados</div></div>
    </div>

    <div class="sect"><h3>Verificación mecánica de citas</h3>
      <div class="card pad">
        <p style="margin:0 0 13px;font-size:13.5px;color:var(--ink-2)">
          Cada cita se compara por <b>coincidencia exacta de subcadena</b> contra el texto extraído y
          congelado del PDF, tras normalizar ligaduras tipográficas (<code>ﬁ</code>, <code>ﬂ</code>),
          comillas, guiones de corte de línea y espacios. No es una segunda opinión de un modelo:
          es determinista, y o pasa o no pasa. Una cita que no supere la prueba no se publica.</p>
        <table><thead><tr><th>Prueba sobre MM 5939/2025</th><th>Texto evaluado</th>
          <th style="text-align:right">Resultado</th></tr></thead>
          <tbody>${D.prueba.map(p => `<tr>
            <td style="white-space:nowrap;font-weight:${p.res?600:400}">${esc(p.caso)}</td>
            <td style="font-family:var(--serif);font-size:13px;color:var(--ink-2)">«${p.texto}»</td>
            <td style="text-align:right;white-space:nowrap">${p.res
              ? '<span class="chk">✓ PASA</span>' : '<span class="xmk">✕ FALLA</span>'}</td></tr>`).join('')}
          </tbody></table>
        <p style="margin:13px 0 0;font-size:12.5px;color:var(--ink-3)">
          Cambiar una sola palabra («excede» → «supera») hace fallar la verificación.
          Esa es exactamente la garantía que se busca.</p>
      </div>
    </div>

    <div class="sect"><h3>Alertas activas</h3>
      <div class="grid2">${D.alertas.map(a => `
        <div class="meth" style="border-left:3px solid ${
          a.sev==='serious'?'var(--serious)':a.sev==='warning'?'var(--warn)':'var(--ink-3)'}">
          <span class="badge st-${a.sev}" style="margin-bottom:7px"><span class="dot"></span>${
            a.sev==='serious'?'Acción requerida':a.sev==='warning'?'Atención':'Informativo'}</span>
          <h4>${esc(a.titulo)}</h4>
          <p style="margin-bottom:7px">${esc(a.detalle)}</p>
          <p style="color:var(--ink);font-weight:500">→ ${esc(a.accion)}</p>
        </div>`).join('')}</div>
    </div>

    <div class="sect"><h3>Calendario de vigencias</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Fecha</th><th>Hito</th><th>Impacto sobre el corpus</th></tr></thead>
        <tbody>${D.calendario.map(c => `<tr>
          <td class="m" style="font-weight:600">${c.fecha}</td>
          <td>${esc(c.hito)}</td>
          <td style="color:var(--ink-2);font-size:12.5px">${esc(c.impacto)}</td></tr>`).join('')}</tbody>
      </table></div>
    </div>

    <div class="sect"><h3>Vacíos — documentos citados que no están en el repositorio</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Documento referido</th><th>Citado en</th><th>Materia</th></tr></thead>
        <tbody>${D.vacios.map(v => `<tr>
          <td class="m" style="color:var(--serious-ink);font-weight:600">${esc(v.ref)}</td>
          <td class="m">${esc(v.citado_en)}</td>
          <td style="color:var(--ink-2)">${esc(v.materia)}</td></tr>`).join('')}</tbody>
      </table></div>
      <p style="font-size:12.5px;color:var(--ink-3);margin-top:11px">
        El sistema detecta estas referencias al analizar cada documento. Una cadena de criterio con
        eslabones faltantes se marca como incompleta en vez de presentarse como si estuviera cerrada.</p>
    </div>

    <div class="sect"><h3>Subcarpeta sin contenido</h3>
      <div class="card pad" style="font-size:13.5px;color:var(--ink-2)">
        <b style="color:var(--ink)">DE LA DIRECCIÓN DEL TRABAJO</b> — vacía. Cuatro pronunciamientos del
        corpus citan dictámenes de la DT (N° 1084/013 de 2012, N° 1949/032 de 2021, N° 67/01 de 2024
        y el Oficio N° 355 de 2025) que serían sus contenidos naturales.
      </div>
    </div>`;
}

/* ══ 6 · Arquitectura ════════════════════════════════════ */
function renderArq(){
  const sql = esc(D.esquema)
    .replace(/(--[^\n]*)/g,'<span class="c">$1</span>')
    .replace(/\b(CREATE|TABLE|TYPE|INDEX|PRIMARY KEY|REFERENCES|NOT NULL|UNIQUE|DEFAULT|GENERATED ALWAYS AS|STORED|ON DELETE CASCADE|CHECK|RETURNS|BEGIN|END|IF|THEN|RAISE EXCEPTION|RETURN|LANGUAGE|REVOKE|FROM|OR REPLACE|FUNCTION|USING)\b/g,'<span class="k">$1</span>')
    .replace(/\b(bigserial|smallserial|serial|bigint|smallint|integer|text|date|timestamptz|boolean|bytea|jsonb|tsvector|trigger|ENUM)\b/g,'<span class="t">$1</span>');
  return document.getElementById('v-arq').innerHTML = `
    <h2 class="vh">Qué se construye en producción</h2>
    <p class="vsub">El prototipo corre sobre datos reales pero con el índice embebido.
    En producción, el índice vive en Postgres y la verificación se ejecuta en el servidor,
    en cada ingesta y en un job nocturno sobre todo el corpus.</p>

    <div class="sect"><h3>Canalización de ingesta</h3>
      <div class="flow">
        <div class="step"><span class="n">01</span><h5>Depósito</h5>
          <p>El PDF llega a la carpeta o se sube por la app. Se calcula sha256 del binario.</p></div>
        <div class="step"><span class="n">02</span><h5>Extracción</h5>
          <p>Texto por página con poppler. OCR sólo si no hay capa de texto. El resultado se congela.</p></div>
        <div class="step"><span class="n">03</span><h5>Propuesta de ficha</h5>
          <p>Se extraen número, fecha, emisor, destinatario, normas citadas y candidatos a cita.</p></div>
        <div class="step gate"><span class="n">04</span><h5>Verificación</h5>
          <p><b>Compuerta.</b> Cada cita debe coincidir exactamente con el texto congelado.</p></div>
        <div class="step gate"><span class="n">05</span><h5>Revisión del abogado</h5>
          <p><b>Compuerta.</b> Un abogado confirma criterio, fuerza, alcance y relaciones.</p></div>
        <div class="step"><span class="n">06</span><h5>Publicación</h5>
          <p>Se indexa, se disparan alertas de impacto normativo y de tensión, se registra en bitácora.</p></div>
      </div>
      <p style="font-size:12.5px;color:var(--ink-3);margin-top:11px">
        Las dos compuertas son bloqueantes. Nada se publica sin cita verificada y sin firma humana.</p>
    </div>

    <div class="sect"><h3>Modelo de datos — PostgreSQL</h3>
      <pre>${sql}</pre>
      <div class="grid2" style="margin-top:13px">
        <div class="meth"><h4>El criterio es la unidad, no el documento</h4>
          <p>Un memorándum puede contener varios criterios con distinta fuerza. El MM 3129/2022 concluye
          sobre la procedencia, sugiere sobre el correo y recomienda sobre el teléfono: tres registros,
          no uno.</p></div>
        <div class="meth"><h4>La naturaleza distingue lo propio de lo citado</h4>
          <p>El MM 5532/2020 transcribe la tesis de la Gerencia para <i>rechazarla</i>. Marcada como
          <code>desestimado</code>, nunca puede devolverse como criterio de la Fiscalía.</p></div>
        <div class="meth"><h4>El hash convierte el reemplazo silencioso en un error visible</h4>
          <p>Si alguien sustituye el PDF, el sha256 deja de coincidir y todas las citas del documento
          pasan a estado no verificado hasta revalidarse.</p></div>
        <div class="meth"><h4>La regla vive en la base, no en la aplicación</h4>
          <p>El trigger sobre <code>cita</code> impide publicar sin verificar por cualquier vía de
          escritura: API, carga masiva o consola.</p></div>
      </div>
    </div>

    <div class="sect"><h3>API</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Método</th><th>Ruta</th><th>Devuelve</th></tr></thead>
        <tbody>${D.api.map(([m,r,d]) => `<tr>
          <td class="m" style="font-weight:700;color:${m==='GET'?'var(--accent-2)':'var(--serious-ink)'}">${m}</td>
          <td class="m">${esc(r)}</td>
          <td style="color:var(--ink-2)">${esc(d)}</td></tr>`).join('')}</tbody>
      </table></div>
    </div>

    <div class="sect"><h3>Componentes</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Capa</th><th>Tecnología</th><th>Notas de diseño</th></tr></thead>
        <tbody>${D.stack.map(([c,t,n]) => `<tr>
          <td style="font-weight:600;white-space:nowrap">${esc(c)}</td>
          <td class="m">${esc(t)}</td>
          <td style="color:var(--ink-2)">${esc(n)}</td></tr>`).join('')}</tbody>
      </table></div>
    </div>

    <div class="sect"><h3>Plan por fases</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Fase</th><th>Entrega</th><th>Contenido</th><th>Estimación</th></tr></thead>
        <tbody>${D.fases.map(([f,e,c,t],i) => `<tr${i===0?' style="background:var(--accent-soft)"':''}>
          <td class="m" style="font-weight:700;color:var(--accent-2)">${esc(f)}</td>
          <td style="font-weight:600;white-space:nowrap">${esc(e)}</td>
          <td style="color:var(--ink-2)">${esc(c)}</td>
          <td class="m" style="white-space:nowrap">${esc(t)}</td></tr>`).join('')}</tbody>
      </table></div>
    </div>

    <div class="sect"><h3>Límite de diseño</h3>
      <div class="card pad" style="border-left:3px solid var(--accent)">
        <p style="margin:0 0 9px;font-size:14px"><b>La aplicación localiza y ordena; no concluye.</b></p>
        <p style="margin:0;font-size:13.5px;color:var(--ink-2)">
          La respuesta a «¿qué se ha dicho sobre X?» es una cronología con citas verificadas, jerarquía,
          fuerza y alcance, más la declaración explícita de lo que <i>no</i> está cubierto. La exportación
          a Word entrega un armazón —antecedentes, marco normativo, criterio previo, vacíos— y nunca
          una conclusión redactada. El juicio jurídico sigue siendo del abogado, y la trazabilidad
          existe para que pueda ejercerlo sobre material verificable.</p>
      </div>
    </div>

    <div class="sect"><h3>Advertencia sobre datos personales</h3>
      <div class="card pad" style="border-left:3px solid var(--warn)">
        <p style="margin:0;font-size:13.5px;color:var(--ink-2)">
          El corpus contiene nombres, RUN, domicilios, predios y razones sociales. Desde el
          <b>1 de diciembre de 2026</b> le son aplicables a la propia aplicación las obligaciones de la
          <b>Ley 21.719</b>, con el estándar que fija el MM 4187/2026: control de acceso por perfiles,
          trazabilidad de accesos, plazos de conservación determinados y evaluación de impacto previa.
          Conviene definir desde el diseño qué campos se anonimizan en las salidas y quién accede al
          índice completo.</p>
      </div>
    </div>`;
}

/* ══ Navegación ══════════════════════════════════════════ */
const VIEWS = [
  ['consulta','Consulta', renderConsulta],
  ['lineas','Líneas de criterio', renderLineas],
  ['corpus','Corpus', renderCorpus],
  ['normas','Normas', renderNormas],
  ['control','Control', renderControl],
  ['arq','Arquitectura', renderArq],
];
const nav = document.getElementById('nav');
nav.innerHTML = VIEWS.map(([k,l],i) =>
  `<button role="tab" aria-selected="${i===0}" data-k="${k}">${l}</button>`).join('');
const hecho = new Set();
function ir(k){
  VIEWS.forEach(([kk,,fn]) => {
    document.getElementById('v-'+kk).classList.toggle('on', kk===k);
    if (kk===k && !hecho.has(kk)){ fn(); hecho.add(kk); }
  });
  nav.querySelectorAll('button').forEach(b => b.setAttribute('aria-selected', b.dataset.k===k));
  window.scrollTo({top:0,behavior:'smooth'});
}
nav.querySelectorAll('button').forEach(b => b.onclick = () => ir(b.dataset.k));
renderConsulta(); hecho.add('consulta');
</script>

<div style="max-width:1180px;margin:0 auto;padding:0 28px 40px">
  <div class="foot">
    <span>Prototipo funcional · 20 documentos reales de la carpeta Pronunciamientos ·
      20/20 citas verificadas mecánicamente</span>
    <span>Fiscalía · Corporación Nacional Forestal · agosto 2026</span>
  </div>
</div>
</body></html>"""

out = HTML.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False))
with io.open("/tmp/pron/app/prototipo-fiscalia.html", "w", encoding="utf-8") as f:
    f.write(out)
print("OK", os.path.getsize("/tmp/pron/app/prototipo-fiscalia.html"), "bytes")
