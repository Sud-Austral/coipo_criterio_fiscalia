# -*- coding: utf-8 -*-
"""Construye el índice completo: documentos, pasajes, materias, citas y vacíos."""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nucleo as N
from nucleo import normalizar, plegar, raiz, raices
from tesauro import TESAURO, AUTORIDADES, PESO_FRASE, PESO_PALABRA, UMBRAL, preferido
from dataset import DOCS as META, RUTAS

# ── etiquetado de pasajes por tesauro, con peso de evidencia ──────────
FRASES, PALABRAS = [], []
for materia, d in TESAURO.items():
    for t in [materia] + d.get("frases", []):
        p = plegar(t)
        if p and " " in p: FRASES.append((materia, p, t))
    for t in d.get("palabras", []):
        p = plegar(t)
        if p: PALABRAS.append((materia, raiz(p), t))

def materias_de(texto):
    """Materias activadas, con la evidencia que las sostiene.
    Una frase basta (peso 2); dos palabras distintas también (1+1)."""
    pl = " " + plegar(texto) + " "
    rz = raices(texto)
    ev = {}
    for materia, p, orig in FRASES:
        if f" {p} " in pl:
            ev.setdefault(materia, {"peso": 0, "por": []})
            ev[materia]["peso"] += PESO_FRASE
            ev[materia]["por"].append(f"frase: {orig}")
    for materia, r, orig in PALABRAS:
        if r in rz:
            ev.setdefault(materia, {"peso": 0, "por": []})
            ev[materia]["peso"] += PESO_PALABRA
            ev[materia]["por"].append(f"término: {orig}")
    return {m: v for m, v in ev.items() if v["peso"] >= UMBRAL}

RE_NORMA = re.compile(
    r"(Ley\s+N?[°º]?\s*[\d.]+|Ley\s+de\s+Presupuestos|Código\s+(?:Civil|del\s+Trabajo)|"
    r"D\.?L\.?\s+N?[°º]?\s*[\d.]+|D\.?S\.?\s+N?[°º]?\s*[\d.]+|DFL\s+N?[°º]?\s*\d+|"
    r"Decreto\s+N?[°º]?\s*[\d.]+|Constitución|Carta\s+Fundamental|Convención\s+de\s+Washington)"
    r"(?:[^.;)\n]{0,40}?(art(?:ículo|\.)\s*[\d]+\s*(?:bis|ter|quáter|quater|quinquies|sexies)?))?",
    re.I)

def normalizar_norma(txt):
    t = re.sub(r"\s+", " ", txt).strip(" .,;")
    t = re.sub(r"N[°º]\s*", "", t)
    t = t.replace("D.L.", "DL").replace("D.S.", "DS").replace("D. S.", "DS")
    t = re.sub(r"^Carta Fundamental$", "Constitución", t, flags=re.I)
    return t[:1].upper() + t[1:]

RE_ART = re.compile(r"artículo|art\.", re.I)

def normas_de(texto):
    out = set()
    for m in RE_NORMA.finditer(texto):
        cuerpo = normalizar_norma(m.group(1))
        art = m.group(2)
        if art:
            art = RE_ART.sub("art.", art).strip()
            out.add(cuerpo + " " + art)
        else:
            out.add(cuerpo)
    return sorted(out)

def recortar_contiguo(texto, fuente_norm):
    """Garantiza que el pasaje sea subcadena LITERAL y contigua del fuente.

    Al limpiar encabezados de impresión que caen a mitad de un pasaje (los que
    cruzan un corte de página), el texto resultante puede dejar de existir de
    forma contigua en el original. Para una herramienta jurídica eso es
    inaceptable: se recorta al tramo que sí es contiguo y se cierra en límite
    de oración o de palabra. Convierte la verificación V02 en una garantía
    estructural en vez de una comprobación que a veces falla.
    """
    t = normalizar(texto)
    if t in fuente_norm:
        return t
    lo, hi = 0, len(t)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if t[:mid] in fuente_norm: lo = mid
        else: hi = mid - 1
    frag = t[:lo]
    corte = frag.rfind(". ")
    if corte > 120:
        frag = frag[:corte + 1]
    else:
        frag = frag[:frag.rfind(" ")] if " " in frag else frag
    return frag.strip()


def marcar_principal(ps, cita_n):
    for p in ps:
        if cita_n in normalizar(p["texto"]):
            p["principal"] = True
            return True
    return False


def pasaje_por_cita(slug, crudo, cita_n, orden):
    """Construye un pasaje anclado a la cita, con contexto de oración completa."""
    offs = N.paginas_offsets(crudo)
    # localizar la cita sobre el crudo normalizado por ventanas
    plano = normalizar(crudo)
    i = plano.find(cita_n)
    if i < 0:
        return None
    # Ventana de contexto recortada SIEMPRE a límite de oración, nunca a
    # mitad de palabra: se busca hacia atrás desde el inicio de la cita y
    # hacia adelante desde su fin.
    ini_busq = max(0, i - 340)
    izq = plano.rfind(". ", ini_busq, i)
    ini = izq + 2 if izq != -1 else (plano.rfind(" ", ini_busq, i) + 1 if i > 340 else 0)
    fin_cita = i + len(cita_n)
    der = plano.find(". ", fin_cita, min(len(plano), fin_cita + 340))
    fin = der + 1 if der != -1 else fin_cita
    frag = plano[ini:fin]
    # página: se busca sobre el crudo para no perder el ancla física
    bruto_i = crudo.find(cita_n[:40].split(" ", 1)[0])
    return {"doc": slug, "orden": orden, "etiqueta": "cita",
            "texto": frag.strip(), "pagina": N.pagina_en(offs, max(bruto_i, 0)),
            "offset": max(bruto_i, 0)}


# ── construcción ──────────────────────────────────────────────────────
def construir():
    textos = N.cargar_textos()
    meta = {d["id"]: d for d in META}
    # el dataset usa CGR-E337332-2023 / CPLT-C7949-21 con otros ids
    alias = {"CGR-E337332-2023": "E337332-2023", "CPLT-C7949-21": "CPLT-C7949-21"}

    docs, pasajes = [], []
    for slug, crudo in textos.items():
        mid = alias.get(slug, slug)
        m = meta[mid]
        fuente_norm = normalizar(crudo)
        ps = []
        for p in N.extraer_pasajes(slug, crudo):
            p["texto"] = recortar_contiguo(p["texto"], fuente_norm)
            if len(p["texto"]) >= N.MIN_LARGO:
                p["orden"] = len(ps) + 1
                ps.append(p)
        for p in ps:
            p["id"] = f"{slug}#{p['orden']}"
            p["materias"] = materias_de(p["texto"])
            p["normas"] = normas_de(p["texto"])
            p["refs"] = sorted({k for k, _ in N.refs_de(p["texto"])})
            p["principal"] = False
            pasajes.append(p)
        # El pasaje que contiene la cita curada es el criterio principal.
        # Si la segmentación lo partió, se construye un pasaje anclado a la cita:
        # ningún documento puede quedar sin su criterio principal indexado.
        cita_n = normalizar(m["cita"])
        if not marcar_principal(ps, cita_n):
            extra = pasaje_por_cita(slug, crudo, cita_n, len(ps) + 1)
            if extra:
                extra["id"] = f"{slug}#{extra['orden']}"
                extra["materias"] = materias_de(extra["texto"])
                extra["normas"] = normas_de(extra["texto"])
                extra["refs"] = sorted({k for k, _ in N.refs_de(extra["texto"])})
                extra["principal"] = True
                ps.append(extra); pasajes.append(extra)
        d = dict(m); d["id"] = slug
        # los descriptores se normalizan al vocabulario único del tesauro
        d["descriptores_originales"] = list(m["descriptores"])
        d["descriptores"] = sorted({preferido(x) for x in m["descriptores"]})
        d["ruta"] = RUTAS[mid]
        pri = [x for x in ps if x["principal"]]
        d["pagina"] = pri[0]["pagina"] if pri else None
        d["sha"] = (N.sha_pdf(RUTAS[mid]) or "")[:16]
        d["paginas"] = crudo.count("\f") + 1
        d["n_pasajes"] = len(ps)
        d["refs"] = sorted({k for k, _ in N.refs_de(normalizar(crudo))})
        d["materias_texto"] = sorted({mm for p in ps for mm in p["materias"]})

        # ── Fuente única para las normas ─────────────────────────────
        # Había dos listas para lo mismo: la curada en la ficha (77 entradas)
        # y la extraída del texto (48), con solo 10 en común. Distintas vistas
        # leían distintas listas. Se fusionan en un solo índice con procedencia
        # y con la página donde el extractor la vio, para que toda vista lea
        # exactamente lo mismo y se pueda ir al PDF.
        pag_de = {}
        for p in ps:
            for n in p["normas"]:
                pag_de.setdefault(n, p["pagina"])
        curadas, extraidas = set(m["normas"]), set(pag_de)
        d["normas_idx"] = [
            {"n": n,
             "origen": ("ambas" if n in curadas and n in extraidas
                        else "ficha" if n in curadas else "texto"),
             "pagina": pag_de.get(n)}
            for n in sorted(curadas | extraidas)
        ]
        docs.append(d)
    docs.sort(key=lambda d: d["fecha"])

    # ── cierre de citas ───────────────────────────────────────────────
    en_corpus = {d["id"] for d in docs}
    # equivalencias entre la clave detectada y el slug del corpus
    equiv = {}
    for d in docs:
        mm = re.match(r"(MM|OF|RES)-(\d+)-(\d{4})", d["id"])
        if mm: equiv[f"{mm.group(1)}-{mm.group(2)}-{mm.group(3)}"] = d["id"]
    equiv["CGR-337332"] = "CGR-E337332-2023"

    etiqueta = {}
    for slug, crudo in textos.items():
        for k, lab in N.refs_de(normalizar(crudo)):
            etiqueta.setdefault(k, lab)

    # Clasificación de la referencia: no todo vacío pesa lo mismo. El memo que
    # originó la consulta es trámite; un dictamen de la CGR es doctrina que
    # sostiene el criterio. Mezclarlos vuelve inútil la lista de vacíos.
    APERTURA = 900        # caracteres iniciales del cuerpo = fórmula de solicitud

    citas = {}
    for d in docs:
        crudo_n = normalizar(textos[d["id"]])
        cuerpo = re.split(r"\bc\.c\.:|\bDistribución:", crudo_n)[0]
        # el cuerpo real empieza tras el encabezado MATERIA/FECHA
        mm = re.search(r"FECHA\s*:\s*\d{2}/\d{2}/\d{4}|SANTIAGO,\s*\d{2}/\d{2}/\d{4}", cuerpo)
        arranque = cuerpo[mm.end(): mm.end() + APERTURA] if mm else cuerpo[:APERTURA]
        claves_apertura = {k for k, _ in N.refs_de(arranque)}
        for k in d["refs"]:
            destino = equiv.get(k, k if k in en_corpus else None)
            if destino == d["id"]:
                continue                       # autorreferencia
            if k.startswith("CGR-"):
                clase = "doctrina externa"
            elif k in claves_apertura:
                clase = "solicitud / trámite"
            elif k.startswith(("OF-", "RES-")):
                clase = "instrucción CONAF"
            else:
                clase = "documento citado"
            e = citas.setdefault(k, {"clave": k,
                    "etiqueta": AUTORIDADES.get(k, {}).get("nombre") or etiqueta.get(k, k),
                    "en_corpus": bool(destino), "destino": destino,
                    "citado_por": [], "clases": []})
            e["citado_por"].append(d["id"])
            e["clases"].append(clase)
    ORDEN_CLASE = {"doctrina externa": 0, "instrucción CONAF": 1,
                   "documento citado": 2, "solicitud / trámite": 3}
    for e in citas.values():
        e["citado_por"] = sorted(set(e["citado_por"]))
        e["clase"] = sorted(set(e["clases"]), key=lambda c: ORDEN_CLASE[c])[0]
        del e["clases"]
        if e["clave"] in AUTORIDADES:
            a = AUTORIDADES[e["clave"]]
            e["doctrina"] = a["doctrina"]; e["variantes"] = a["variantes"]
            e["critico"] = a.get("clave", False)

    vacios = sorted([e for e in citas.values() if not e["en_corpus"]],
                    key=lambda e: (ORDEN_CLASE[e["clase"]], -len(e["citado_por"]), e["etiqueta"]))

    return {"docs": docs, "pasajes": pasajes,
            "citas": sorted(citas.values(), key=lambda e: e["etiqueta"]),
            "vacios": vacios, "equiv": equiv}


if __name__ == "__main__":
    idx = construir()
    json.dump(idx, open("/tmp/pron/app/indice.json", "w"), ensure_ascii=False, indent=1)
    print(f"documentos ........ {len(idx['docs'])}")
    print(f"pasajes ........... {len(idx['pasajes'])}")
    print(f"  principales ..... {sum(1 for p in idx['pasajes'] if p['principal'])}")
    print(f"referencias ....... {len(idx['citas'])}")
    print(f"  incorporadas .... {sum(1 for c in idx['citas'] if c['en_corpus'])}")
    print(f"  VACÍOS .......... {len(idx['vacios'])}")
    print(f"materias activas .. {len({m for p in idx['pasajes'] for m in p['materias']})}")
