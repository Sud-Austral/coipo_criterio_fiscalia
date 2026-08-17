# -*- coding: utf-8 -*-
"""
Auditoría de consistencia entre vistas.

Pregunta que responde: ¿toda cifra, rótulo y relación que el prototipo muestra
sale del índice único, o hay vistas alimentadas por datos escritos a mano que
quedaron desfasados?

Es el mismo defecto que ya apareció dos veces —dos vocabularios de materias,
dos fuentes de normas— y por eso merece comprobación mecánica en vez de
inspección visual.
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

IDX = json.load(open("/tmp/pron/app/indice.json", encoding="utf-8"))
JS  = open("/tmp/pron/app/app.js", encoding="utf-8").read()
sys.path.insert(0, "/tmp/pron/app")
from build import LINEAS, ALERTAS, CALENDARIO
from tesauro import TESAURO

DOCS = {d["id"]: d for d in IDX["docs"]}
PAS  = IDX["pasajes"]
FALLOS = []

def check(codigo, titulo, fallos, total, glosa):
    FALLOS.append({"codigo": codigo, "titulo": titulo, "fallos": fallos,
                   "total": total, "glosa": glosa})

# ── C1 · Campos leídos por las vistas que existen en el índice ────────
campos_doc = set(re.findall(r"(?<![a-zA-Z.])d\.([a-z_]+)", JS)) | set(re.findall(r"\.doc\.([a-z_]+)", JS))
campos_pas = set(re.findall(r"(?<![a-zA-Z.])p\.([a-z_]+)", JS))
CLAVES_DOC = set().union(*[set(d) for d in IDX["docs"]])
CLAVES_PAS = set().union(*[set(x) for x in PAS])
LOCALES = {"caso", "res", "texto", "endsWith", "ends", "frases", "palabras", "sev"}
raiz_D     = set(re.findall(r"\bD\.([a-zA-Z_]+)", JS))
PAYLOAD = {"docs","pasajes","citas","vacios","integridad","tesauro","autoridades",
           "umbral","lineas","alertas","calendario","api","stack","fases","prueba",
           "estadoMeta","jerarquiaMeta","fuerzaMeta","esquema"}
IGNORAR = {"map","filter","forEach","length","find","slice","some","every","join",
           "sort","push","split","replace","includes","reduce","values","keys","entries"}
f = sorted((campos_doc - CLAVES_DOC - IGNORAR - LOCALES) |
           {"p."+x for x in (campos_pas - CLAVES_PAS - IGNORAR - LOCALES)} |
           {"D."+x for x in (raiz_D - PAYLOAD - IGNORAR)})
check("C1", "Campos leídos existen en el índice", f,
      len(campos_doc | campos_pas | raiz_D), "referencias a campos inexistentes o desfasados")

# ── C2 · Los nodos de las líneas de criterio existen ──────────────────
f = [f"{L['id']}: {n.get('id')}" for L in LINEAS for n in L["nodos"]
     if n["tipo"] == "doc" and n["id"] not in DOCS]
check("C2", "Nodos de líneas apuntan al corpus", f,
      sum(len(L["nodos"]) for L in LINEAS), "documentos citados en las cadenas que existen")

# ── C3 · Las relaciones dibujadas coinciden con las del índice ────────
f, tot = [], 0
for L in LINEAS:
    docs_linea = [n["id"] for n in L["nodos"] if n["tipo"] == "doc"]
    for i in range(len(docs_linea) - 1):
        tot += 1
        a, b = docs_linea[i], docs_linea[i + 1]
        rels = {r["ref"] for r in DOCS[b].get("relaciones", [])} | \
               {r["ref"] for r in DOCS[a].get("relaciones", [])}
        if a not in rels and b not in rels:
            f.append(f"{L['id']}: {a} → {b} sin relación declarada en la ficha")
check("C3", "Cadenas respaldadas por relaciones de ficha", f, tot,
      "eslabones consecutivos con relación declarada en el índice")

# ── C4 · Las alertas coinciden con el estado calculado ────────────────
f = []
for a in ALERTAS:
    ref = a.get("ref")
    if ref and ref not in DOCS:
        f.append(f"«{a['titulo']}» apunta a {ref}, que no está en el índice")
    elif ref and a["sev"] == "serious" and DOCS[ref]["estado"] != "requiere_revision":
        f.append(f"«{a['titulo']}» marca acción requerida pero {ref} está «{DOCS[ref]['estado']}»")
esperadas = {d["id"] for d in IDX["docs"] if d["estado"] in
             ("requiere_revision", "vigencia_diferida", "consulta_pendiente")}
cubiertas = {x for a in ALERTAS for x in (a.get("refs") or [a.get("ref")]) if x}
sin_alerta = sorted(esperadas - cubiertas)
f += [f"{x} tiene estado «{DOCS[x]['estado']}» y ninguna alerta lo menciona" for x in sin_alerta]
check("C4", "Alertas reflejan el estado del índice", f, len(ALERTAS) + len(esperadas),
      "alertas consistentes con los estados calculados")

# ── C5 · Cifras afirmadas en los textos de la interfaz ────────────────
# Una cifra escrita como ${D...} está calculada: es lo que se busca.
CALCULADAS = len(re.findall(r"\$\{D\.\w+[^}]*\.length", JS))
afirmaciones = [
    (r"La <b>Ley 19\.628</b> sostiene (\d+) pronunciamientos",
     len({d["id"] for d in IDX["docs"] if any(n.startswith("Ley 19.628") for n in d["normas"])})),
    (r"invocado por (\d+) pronunciamientos",
     len(next(v for v in IDX["vacios"] if v["clave"] == "CGR-33624")["citado_por"])),
    (r"De (\d+) referencias, solo", len(IDX["citas"])),
]
f = []
for patron, real in afirmaciones:
    m = re.search(patron, JS)
    if not m:
        continue                      # la cifra no está escrita: se calcula
    elif int(m.group(1)) != real:
        f.append(f"la interfaz dice {m.group(1)} y el índice calcula {real}: {patron[:44]}…")
check("C5", "Cifras del texto coinciden con el índice", f, len(afirmaciones),
      f"cifras escritas a mano contrastadas; otras {CALCULADAS} se interpolan del índice")

# ── C6 · Una sola fuente para las normas ──────────────────────────────
# La regla: ninguna vista lee la lista curada cruda («d.normas»); todas leen el
# índice fusionado «d.normas_idx», que declara procedencia y página. La lista
# extraída del pasaje («p.normas») sí es legítima: es la vía de búsqueda por
# norma, anclada a su propio pasaje.
crudo = re.findall(r"\bd\.normas(?!_idx)\b", JS)
unificado = "normas_idx" in JS
f = []
if crudo:
    f.append(f"{len(crudo)} lectura(s) de la lista curada cruda «d.normas»")
if not unificado:
    f.append("no existe el índice fusionado «normas_idx»")
n_idx = sum(len(d.get("normas_idx", [])) for d in IDX["docs"])
amb = sum(1 for d in IDX["docs"] for x in d.get("normas_idx", []) if x["origen"] == "ambas")
check("C6", "Fuente única para las normas", f, 1,
      f"índice fusionado de {n_idx} entradas, {amb} confirmadas en ficha y texto")

# ── C7 · Vocabulario del tesauro cubre las materias mostradas ─────────
mostradas = {m for p in PAS for m in p["materias"]} | \
            {t for d in IDX["docs"] for t in d["descriptores"]}
f = sorted(mostradas - set(TESAURO))
check("C7", "Materias mostradas están en el tesauro", f, len(mostradas),
      "toda materia visible es un término preferido")


def main():
    rojos = 0
    ancho = max(len(c["titulo"]) for c in FALLOS)
    for c in FALLOS:
        ok = not c["fallos"]
        if not ok: rojos += 1
        print(f"  {'✓ OK   ' if ok else '✗ FALLA'}  {c['codigo']}  {c['titulo']:<{ancho}}  "
              f"{c['total']-len(c['fallos'])}/{c['total']}  {c['glosa']}")
        for x in c["fallos"][:6]:
            print(f"            → {x}")
        if len(c["fallos"]) > 6:
            print(f"            → … y {len(c['fallos'])-6} más")
    print(f"\n  {len(FALLOS)-rojos}/{len(FALLOS)} comprobaciones de consistencia en verde"
          + (f" · {rojos} EN ROJO" if rojos else ""))
    json.dump(FALLOS, open("/tmp/pron/app/consistencia.json", "w"),
              ensure_ascii=False, indent=1, default=str)
    return 1 if rojos else 0


if __name__ == "__main__":
    sys.exit(main())
