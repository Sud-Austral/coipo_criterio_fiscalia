# -*- coding: utf-8 -*-
"""
Núcleo del repositorio: normalización, extracción de pasajes, tesauro,
identidad canónica de autoridades y cierre de citas.

Principio: nada se afirma que no pueda comprobarse contra el texto fuente.
Todo pasaje se extrae POR CONSTRUCCIÓN desde el texto congelado — su cita
literal no puede diferir del original porque es una subcadena de él, y la
suite de integridad lo vuelve a comprobar de todos modos.
"""
import glob, os, re, json, hashlib, unicodedata
from collections import defaultdict

TXT_DIR = "/tmp/pron/txt"
PDF_DIR = "/mnt/user-data/uploads/Pronunciamientos"

# ─────────────────────────────────────────────────────────────────────
# Normalización
# ─────────────────────────────────────────────────────────────────────
LIGADURAS = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}
TIPOGRAF  = {"“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-",
             "−": "-", " ": " ", "º": "°", "’": "'"}

def normalizar(s: str) -> str:
    """Normalización canónica para comparación exacta de citas."""
    for k, v in LIGADURAS.items(): s = s.replace(k, v)
    for k, v in TIPOGRAF.items():  s = s.replace(k, v)
    s = unicodedata.normalize("NFC", s)
    # El guion al final de línea se conserva: en este corpus las 6 ocurrencias
    # son guiones con significado (jurídico-administrativo, 075-2020), ninguna
    # es corte silábico. Borrarlo produciría «jurídicoadministrativo».
    s = re.sub(r"-\s*\n\s*", "-", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def plegar(s: str) -> str:
    """Plegado para búsqueda: sin tildes, minúsculas, sin puntuación."""
    s = normalizar(s).lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ ]+", " ", s)

# Derivación mínima y deliberadamente conservadora. El lematizador resuelve
# MORFOLOGÍA (singular/plural, nominalizaciones); la SINONIMIA la resuelve el
# tesauro. Mezclar ambas cosas en el lematizador es lo que produce falsos
# positivos: una lista de sufijos agresiva convertía «naturales» en «natur» y
# «natural» en «natural», de modo que la consulta «monumento natural» no
# calzaba con el término preferido «Monumentos naturales».
DERIVATIVOS = ("cion", "miento", "idad", "mente", "ancia", "encia")

def raiz(p: str) -> str:
    """Lematizador ligero para español. En producción lo hace Postgres con
    to_tsvector('spanish'); aquí se replica su comportamiento esencial."""
    if len(p) <= 3: return p
    # 1 · plural. En español el plural es -s tras vocal y -es tras consonante:
    # se quita la «s» y, sólo si queda una «e» sostenida por una consonante que
    # exige -es (l, r, n, d, z, j, y), se quita también. Así «naturales»→natural
    # y «leyes»→ley, sin romper «bases»→base ni «informes»→informe.
    if p.endswith("ces") and len(p) > 4:
        p = p[:-3] + "z"
    elif p.endswith("s") and len(p) > 3:
        p = p[:-1]
        if p.endswith("e") and len(p) > 3 and p[-2] in "lrndzjy":
            p = p[:-1]
    # 2 · nominalizaciones frecuentes
    for suf in DERIVATIVOS:
        if p.endswith(suf) and len(p) - len(suf) >= 4:
            return p[: -len(suf)]
    return p

def raices(texto: str) -> set:
    return {raiz(w) for w in plegar(texto).split() if len(w) > 2}

# ─────────────────────────────────────────────────────────────────────
# Corpus
# ─────────────────────────────────────────────────────────────────────
SLUG = {
 "01":"CGR-E337332-2023","02":"MM-1683-2026","03":"MM-1688-2026","04":"MM-2061-2026",
 "05":"MM-2665-2026","06":"MM-2698-2026","07":"MM-3129-2022","08":"MM-4187-2026",
 "09":"MM-5532-2020","10":"MM-5939-2025","11":"MM-751-2021","12":"MM-862-2021",
 "13":"MM-3171-2026","14":"OF-440-2026","15":"OF-442-2026","16":"OF-444-2026",
 "17":"RES-884-2026","18":"CPLT-C7949-21","19":"MM-3320-2026","20":"MM-3400-2022",
}

def cargar_textos():
    out = {}
    for f in sorted(glob.glob(os.path.join(TXT_DIR, "*.txt"))):
        n = os.path.basename(f).split("_")[0]
        out[SLUG[n]] = open(f, encoding="utf-8").read()
    return out

def sha_pdf(ruta_rel):
    p = os.path.join(PDF_DIR, ruta_rel)
    if not os.path.exists(p): return None
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

# ─────────────────────────────────────────────────────────────────────
# Extracción de pasajes
# ─────────────────────────────────────────────────────────────────────
ORDINALES = ("PRIMERO","SEGUNDO","TERCERO","CUARTO","QUINTO","SEXTO","SÉPTIMO",
             "SEPTIMO","OCTAVO","NOVENO","DÉCIMO","DECIMO","UNDÉCIMO","UNDECIMO",
             "DUODÉCIMO","DUODECIMO")

MARCA = re.compile(
    r"(?:^|\n)\s{0,24}("
    r"(?:" + "|".join(ORDINALES) + r")\s*:"          # PRIMERO:
    r"|\d{1,2}\s*[\.\)]\s"                            # 1. / 2)
    r"|[a-h]\s*\)\s"                                  # a)
    r"|[-–]\s?(?=[A-ZÁÉÍÓÚÑ])"                        # - Conclusión
    r"|(?:I{1,3}|IV|V|VI{0,3}|IX|X)\s*[\.\-]\s(?=[A-ZÁÉÍÓÚ])"   # II. ANÁLISIS
    r")")

RUIDO = re.compile(
    r"(ceropapel\.conaf\.cl|www\.|https?://|^\s*c\.c\.|^\s*Distribución:|"
    r"Saluda (atentamente|cordialmente)|Fecha Publicación|^\s*Adjuntos|"
    r"consejotransparencia|Morandé 360|^Página \d)", re.I | re.M)

MIN_LARGO, MAX_LARGO = 130, 1600

def paginas_offsets(crudo):
    """Devuelve [(inicio, fin, n_pagina)] sobre el texto crudo."""
    out, pos, n = [], 0, 1
    for parte in crudo.split("\f"):
        out.append((pos, pos + len(parte), n))
        pos += len(parte) + 1
        n += 1
    return out

def pagina_en(offs, i):
    for a, b, n in offs:
        if a <= i <= b: return n
    return offs[-1][2] if offs else 1

def limpiar(t):
    """Quita encabezados de impresión y pies de página del pasaje."""
    t = re.sub(r"\n?\s*\d{1,2}/\d{1,2}/\d{2},\s*\d{1,2}:\d{2}\s*[^\n]*", " ", t)
    t = re.sub(r"https?://\S+\s*\d*/\d*", " ", t)
    t = re.sub(r"\n\s*\d+/\d+\s*\n", " ", t)
    return normalizar(t)

def extraer_pasajes(slug, crudo):
    offs = paginas_offsets(crudo)
    marcas = [(m.start(1), m.group(1).strip()) for m in MARCA.finditer(crudo)]
    marcas.append((len(crudo), ""))
    pasajes = []
    for i in range(len(marcas) - 1):
        ini, etiqueta = marcas[i]
        fin = marcas[i + 1][0]
        bruto = crudo[ini:fin]
        if RUIDO.search(bruto[:200]):
            continue
        texto = limpiar(bruto)
        # descartar la etiqueta suelta y los fragmentos triviales
        cuerpo = texto[len(etiqueta):].strip(" .:-")
        if not (MIN_LARGO <= len(cuerpo) <= MAX_LARGO):
            continue
        if len(re.findall(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+ [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+", cuerpo)) > 6:
            continue                     # lista de nombres, no criterio
        if cuerpo.count("@") or re.search(r"Jefe \(I\)|Abogad[oa] |Secretari", cuerpo):
            continue
        pasajes.append({
            "doc": slug,
            "orden": len(pasajes) + 1,
            "etiqueta": etiqueta.strip(" .:)") or "—",
            "texto": cuerpo,
            "pagina": pagina_en(offs, ini),
            "offset": ini,
        })
    # Respaldo: los documentos redactados en prosa continua no traen marcas de
    # enumeración. Sin esto quedarían con cero pasajes, es decir, invisibles —
    # que es exactamente el modo de fallo que la herramienta debe cerrar.
    if len(pasajes) < 2:
        pasajes = extraer_parrafos(slug, crudo, offs)
    return pasajes


def extraer_parrafos(slug, crudo, offs):
    """Segmentación por párrafo para documentos sin enumeración."""
    pasajes, pos = [], 0
    for bloque in re.split(r"\n\s*\n", crudo):
        ini = crudo.find(bloque, pos)
        pos = ini + len(bloque) if ini >= 0 else pos
        if ini < 0: ini = pos
        if RUIDO.search(bloque[:200]):
            continue
        cuerpo = limpiar(bloque).strip(" .:-")
        if not (MIN_LARGO <= len(cuerpo) <= MAX_LARGO):
            continue
        if len(re.findall(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+ [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+", cuerpo)) > 6:
            continue
        if re.search(r"Jefe \(I\)|Abogad[oa] Fiscal|Secretari[ao] ", cuerpo):
            continue
        pasajes.append({
            "doc": slug, "orden": len(pasajes) + 1, "etiqueta": "¶",
            "texto": cuerpo, "pagina": pagina_en(offs, ini), "offset": ini,
        })
    return pasajes

# ─────────────────────────────────────────────────────────────────────
# Identidad canónica de autoridades
# ─────────────────────────────────────────────────────────────────────
def canon_dictamen(num: str) -> str:
    """E33624, 33624, 33.624 → CGR-33624. Una autoridad, una identidad."""
    d = re.sub(r"[^0-9]", "", num)
    return f"CGR-{int(d)}" if d else f"CGR-{num}"

RE_DICTAMEN = re.compile(
    r"[Dd]ictamen(?:es)?\s+(?:N[°º]?\s*)?(E?\s?\d[\d.]*)"
    r"|[Dd]ictamen\s+(E\d+)N(\d\d)"
    r"|(?:Oficio|Of\.)\s+N[°º]?\s*(E\d{4,})")

RE_INTERNO = re.compile(
    r"(Memor[áa]nd?um|Memo|Oficio|Ord(?:inario)?|Res(?:oluci[óo]n)?)\s*"
    r"(?:Ord\.?\s*)?N?[°º]?\s*(\d{1,4})\s*(?:/|,?\s*de\s+(?:fecha\s+)?)?\s*"
    r"(?:\d{1,2}\s+de\s+\w+\s+de\s+)?(20\d\d|19\d\d)", re.I)

TIPO_INT = {"memorándum":"MM","memorandum":"MM","memorandúm":"MM","memo":"MM",
            "oficio":"OF","ord":"OF","ordinario":"OF","res":"RES",
            "resolución":"RES","resolucion":"RES"}

def refs_de(texto_norm):
    """Referencias salientes: (clave_canónica, etiqueta legible)."""
    cuerpo = re.split(r"\bc\.c\.:|\bDistribución:", texto_norm)[0]
    out = set()
    for m in RE_DICTAMEN.finditer(cuerpo):
        num = m.group(1) or m.group(2) or m.group(4)
        if not num: continue
        num = num.replace(" ", "")
        if len(re.sub(r"\D", "", num)) < 3: continue
        out.add((canon_dictamen(num), f"Dictamen {num}"))
    for m in RE_INTERNO.finditer(cuerpo):
        t = TIPO_INT.get(m.group(1).lower().strip(". "))
        if not t: continue
        out.add((f"{t}-{m.group(2)}-{m.group(3)}", f"{t} {m.group(2)}/{m.group(3)}"))
    return out
