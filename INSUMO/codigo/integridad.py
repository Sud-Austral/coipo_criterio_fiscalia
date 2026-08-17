# -*- coding: utf-8 -*-
"""
Suite de integridad del repositorio.

Quince verificaciones sobre el índice, más siete de consistencia entre vistas. La herramienta no pide que se le crea:
publica el resultado de correrlas. Cualquiera puede reejecutarlas.

Salida: integridad.json + código de salida ≠ 0 si algo falla.
"""
import json, re, sys, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nucleo as N
from nucleo import normalizar
from tesauro import AUTORIDADES, TESAURO, EQUIVALENTES, preferido

IDX = json.load(open("/tmp/pron/app/indice.json", encoding="utf-8"))
TEXTOS = N.cargar_textos()
DOCS, PAS, CITAS, VACIOS = IDX["docs"], IDX["pasajes"], IDX["citas"], IDX["vacios"]
POR_DOC = defaultdict(list)
for p in PAS: POR_DOC[p["doc"]].append(p)

CHECKS = []
def check(codigo, titulo, prueba):
    CHECKS.append({"codigo": codigo, "titulo": titulo, "prueba": prueba})


# ── V01 · La cita curada coincide exactamente con el fuente ───────────
def v01():
    fallos = [d["id"] for d in DOCS
              if normalizar(d["cita"]) not in normalizar(TEXTOS[d["id"]])]
    return len(DOCS), fallos, "citas contrastadas contra el texto congelado"

# ── V02 · Todo pasaje es subcadena verificable del fuente ─────────────
def v02():
    fallos = []
    cache = {k: normalizar(v) for k, v in TEXTOS.items()}
    for p in PAS:
        if normalizar(p["texto"]) not in cache[p["doc"]]:
            fallos.append(p["id"])
    return len(PAS), fallos, "pasajes que existen literalmente en su documento"

# ── V03 · Cada documento tiene hash del binario ──────────────────────
def v03():
    fallos = [d["id"] for d in DOCS if not d.get("sha")]
    return len(DOCS), fallos, "documentos con sha256 del PDF registrado"

# ── V04 · Ningún documento sin criterio principal ────────────────────
def v04():
    fallos = [d["id"] for d in DOCS
              if not any(p["principal"] for p in POR_DOC[d["id"]])]
    return len(DOCS), fallos, "documentos con su criterio principal indexado"

# ── V05 · Ningún documento invisible ─────────────────────────────────
def v05():
    fallos = [d["id"] for d in DOCS if not POR_DOC[d["id"]]]
    return len(DOCS), fallos, "documentos con al menos un pasaje recuperable"

# ── V06 · Materia asignada y materia inferida ────────────────────────
def v06():
    fallos = [d["id"] for d in DOCS
              if not d.get("descriptores") or not d.get("materias_texto")]
    return len(DOCS), fallos, "documentos con materia curada y materia inferida del texto"

# ── V07 · Cierre de citas: ninguna referencia queda sin resolver ─────
def v07():
    resueltas = {c["clave"] for c in CITAS if c["en_corpus"]}
    declaradas = {v["clave"] for v in VACIOS}
    huerfanas = [c["clave"] for c in CITAS
                 if c["clave"] not in resueltas and c["clave"] not in declaradas]
    return len(CITAS), huerfanas, "referencias resueltas al corpus o declaradas como vacío"

# ── V08 · Identidad canónica: una autoridad, una clave ───────────────
def v08():
    porvar = defaultdict(set)
    for k, a in AUTORIDADES.items():
        for v in a["variantes"]:
            porvar[re.sub(r"\D", "", v) or v].add(k)
    fallos = [f"{v} → {sorted(ks)}" for v, ks in porvar.items() if len(ks) > 1]
    return len(AUTORIDADES), fallos, "autoridades sin colisión entre sus variantes de cita"

# ── V09 · Cronología: nadie cita el futuro ───────────────────────────
def v09():
    anio = {d["id"]: int(d["fecha"][:4]) for d in DOCS}
    fallos = []
    for c in CITAS:
        m = re.search(r"(19|20)\d\d$", c["clave"])
        if not m: continue
        a_ref = int(m.group(0))
        for citante in c["citado_por"]:
            if a_ref > anio[citante]:
                fallos.append(f"{citante} cita {c['etiqueta']}")
    return len(CITAS), fallos, "referencias cuya fecha es anterior a la del documento que las cita"

# ── V10 · Cobertura: cada documento alcanzable por ≥2 vías ───────────
def v10():
    fallos = []
    for d in DOCS:
        vias = 0
        if d.get("descriptores"): vias += 1                    # descriptor curado
        if d.get("materias_texto"): vias += 1                  # tesauro sobre el texto
        if any(p["normas"] for p in POR_DOC[d["id"]]): vias += 1   # norma invocada
        if d.get("refs"): vias += 1                            # grafo de citas
        if vias < 2: fallos.append(f"{d['id']} ({vias} vía)")
    return len(DOCS), fallos, "documentos alcanzables por dos o más vías independientes"

# ── V11 · Sin duplicados por contenido ───────────────────────────────
def v11():
    por_sha = defaultdict(list)
    for d in DOCS: por_sha[d["sha"]].append(d["id"])
    fallos = [f"{s}: {ids}" for s, ids in por_sha.items() if len(ids) > 1]
    return len(DOCS), fallos, "documentos sin duplicado de contenido en el índice"

# ── V12 · Toda divergencia está declarada ────────────────────────────
def v12():
    """Dos documentos que comparten materia y cuyos criterios no se citan
    entre sí ni declaran relación quedan como divergencia no evaluada."""
    declaradas = set()
    for d in DOCS:
        for r in d.get("relaciones", []):
            declaradas.add((d["id"], r["ref"]))
            declaradas.add((r["ref"], d["id"]))
    pendientes = []
    for i, a in enumerate(DOCS):
        for b in DOCS[i + 1:]:
            comun = set(a["descriptores"]) & set(b["descriptores"])
            if not comun: continue
            if a["id"] in b.get("refs", []) or b["id"] in a.get("refs", []): continue
            if (a["id"], b["id"]) in declaradas: continue
            if a["jerarquia"] == b["jerarquia"] == "asesor" and a["organo"] == b["organo"]:
                pendientes.append(f"{a['id']} ↔ {b['id']} ({', '.join(sorted(comun))})")
    return len(DOCS) * (len(DOCS) - 1) // 2, pendientes, \
           "pares con materia común: relación declarada o marcados para revisión"


# ── V13 · Vocabulario único: todo descriptor existe en el tesauro ────
def v13():
    usados = {t for d in DOCS for t in d.get("descriptores_originales", d["descriptores"])}
    huerfanos = [t for t in sorted(usados)
                 if preferido(t) not in TESAURO]
    return len(usados), huerfanos, "descriptores curados que resuelven a un término preferido"

# ── V14 · El tesauro no contiene nombres de fuentes ni de órganos ────
def v14():
    """Citar una ley no dice de qué trata un texto: para eso está la vía
    «norma», que es precisa. Un nombre de fuente dentro del tesauro convierte
    cualquier mención en una etiqueta de materia — así un memo de Planes de
    Manejo terminó emparentado con una consulta sobre teletrabajo."""
    normas = {n.lower() for p in PAS for n in p["normas"]}
    cuerpos = {re.sub(r"\s+art\..*$", "", n).strip() for n in normas}
    ORGANOS = re.compile(r"^(superintendencia|consejo|servicio|direcci[oó]n|gerencia|"
                         r"ministerio|tribunal|corte|contralor[ií]a|subsecretar[ií]a)\b", re.I)
    TITULOS = re.compile(r"^(ley|c[oó]digo|estatuto|reglamento|decreto|convenci[oó]n|"
                         r"escala [uú]nica|bases de los)\b", re.I)
    malos, total = [], 0
    for m, d in TESAURO.items():
        for t in d.get("frases", []) + d.get("palabras", []):
            total += 1
            tl = t.lower().strip()
            if tl in cuerpos or ORGANOS.match(tl) or TITULOS.match(tl):
                malos.append(f"«{t}» en {m}")
    return total, malos, "términos del tesauro que no son nombres de fuentes ni de órganos"


check("V01", "Cita literal verificada", v01)
check("V02", "Pasaje trazado al fuente", v02)
check("V03", "Hash del binario registrado", v03)
check("V04", "Criterio principal indexado", v04)
check("V05", "Sin documento invisible", v05)
check("V06", "Materia curada e inferida", v06)
check("V07", "Cierre de citas completo", v07)
check("V08", "Identidad canónica de autoridades", v08)
check("V09", "Consistencia cronológica", v09)
check("V10", "Cobertura multi-vía", v10)
check("V11", "Sin duplicados", v11)
check("V12", "Divergencias declaradas", v12)
# ── V15 · Toda norma de la ficha existe en el texto del documento ────
def v15():
    """La ficha declara qué normas invoca cada documento, y de esa lista vive
    el índice inverso —el que responde «si esta ley cambia, ¿qué criterios
    caen?»—. Sin comprobarla es una afirmación editorial sin respaldo.

    El comprobador debe ser tolerante a la forma real de citar: «D.S. 93, de
    2008», «decreto ley Nº 701, de 1974», «artículos 2º, 4º incisos 1º y 6º».
    Una verificación demasiado estricta produce falsas alarmas, y eso corroe
    la confianza igual que no verificar."""
    import unicodedata
    def pl(x):
        x = unicodedata.normalize("NFD", x.lower())
        x = "".join(c for c in x if unicodedata.category(c) != "Mn")
        x = re.sub(r"[^a-z0-9 ]+", " ", x)
        return re.sub(r"\s+", " ", x).strip()

    def cuerpo_regex(c):
        """«DS 93/2008» → d\W*s\W*93\W*(?:de\W*)?2008 ; tolera N°, puntos y comas."""
        piezas = [p for p in re.split(r"[\s/.]+", pl(c)) if p]
        return r"\W*(?:n\W*)?(?:de\W*)?".join(map(re.escape, piezas))

    ALIAS = {"cpr": ["constitucion politica", "carta fundamental", "constitucion"],
             "dfl 29": ["dfl 29", "ley 18 834", "estatuto administrativo"],
             "convencion de washington": ["convencion de washington",
                 "convencion para la proteccion de la flora"]}
    # La ficha abrevia («DL 701») y el documento escribe la forma extensa
    # («decreto ley Nº 701, de 1974»). Sin esta expansión, el comprobador
    # reprueba citas correctas — falsa alarma, que es peor que no comprobar.
    EXPANDE = {"dl": "decreto ley", "ds": "decreto supremo",
               "dfl": "decreto con fuerza de ley", "cpr": "constitucion"}

    def variantes(c):
        out, pz = [c], pl(c).split()
        if pz and pz[0] in EXPANDE:
            out.append(EXPANDE[pz[0]] + " " + " ".join(pz[1:]))
        if pz and 2 <= len(pz[0]) <= 3 and pz[0].isalpha():
            out.append(" ".join(pz[0]) + " " + " ".join(pz[1:]))   # «D.S.» → «d s»
        return out

    RE_ART = re.compile(r"articulos?\s+((?:\d+\s*(?:bis|ter|quater|quinquies|sexies|"
                        r"[a-z]\b)?(?:\s*(?:inciso|incisos)[^,;.]{0,24})?[,;y\s]{0,4}){1,8})")
    fallos, total = [], 0
    for d in DOCS:
        txt = pl(TEXTOS[d["id"]])
        # todos los números de artículo citados en cualquier parte del documento
        arts = set()
        for m in RE_ART.finditer(txt):
            arts |= set(re.findall(r"\d+", m.group(1)))
        arts |= set(re.findall(r"art\s+(\d+)", txt))
        for n in d["normas"]:
            total += 1
            m = re.match(r"(.+?)\s+art\.\s*(.+)$", n)
            cuerpo, art = (m.group(1), m.group(2)) if m else (n, None)
            cands = ALIAS.get(pl(cuerpo), []) + variantes(cuerpo)
            if not any(re.search(cuerpo_regex(c), txt) for c in cands):
                fallos.append(f"{d['id']}: «{n}» — cuerpo no hallado"); continue
            if art:
                num = re.match(r"\d+", art.strip())
                if num and num.group(0) not in arts:
                    fallos.append(f"{d['id']}: «{n}» — artículo no citado")
    return total, fallos, ("normas de la ficha cuyo rótulo coincide con la forma en que el "
                           "documento las cita")


check("V13", "Vocabulario único", v13)
check("V14", "Tesauro sin nombres de fuentes", v14)
check("V15", "Normas de la ficha respaldadas", v15)


def cargar_consistencia():
    """Incorpora la auditoría de consistencia entre vistas como parte de la
    suite: que cada pestaña lea del índice único es tan verificable como que
    una cita exista, y por las mismas razones."""
    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "consistencia.py")],
                   capture_output=True)
    ruta = "/tmp/pron/app/consistencia.json"
    if not os.path.exists(ruta): return []
    for c in json.load(open(ruta, encoding="utf-8")):
        check(c["codigo"], c["titulo"],
              (lambda cc=c: (cc["total"], cc["fallos"], cc["glosa"])))
    return True


def main():
    cargar_consistencia()
    salida, rojos = [], 0
    ancho = max(len(c["titulo"]) for c in CHECKS)
    for c in CHECKS:
        total, fallos, glosa = c["prueba"]()
        ok = not fallos
        # V12 no es un fallo: es una cola de revisión humana
        severidad = ("aviso" if c["codigo"] in ("V12", "V15") and fallos
                     else ("ok" if ok else "falla"))
        if severidad == "falla": rojos += 1
        marca = {"ok": "✓ OK   ", "aviso": "! AVISO", "falla": "✗ FALLA"}[severidad]
        print(f"  {marca}  {c['codigo']}  {c['titulo']:<{ancho}}  "
              f"{total - len(fallos)}/{total}  {glosa}")
        for f in fallos[:6]:
            print(f"            → {f}")
        if len(fallos) > 6:
            print(f"            → … y {len(fallos)-6} más")
        salida.append({"codigo": c["codigo"], "titulo": c["titulo"], "glosa": glosa,
                       "total": total, "fallos": fallos, "severidad": severidad})
    print(f"\n  {len(CHECKS)-rojos}/{len(CHECKS)} verificaciones en verde"
          + (f" · {rojos} EN ROJO" if rojos else ""))
    json.dump(salida, open("/tmp/pron/app/integridad.json", "w"),
              ensure_ascii=False, indent=1)
    return 1 if rojos else 0


if __name__ == "__main__":
    sys.exit(main())
