# -*- coding: utf-8 -*-
"""Genera el prototipo v2: búsqueda multi-vía, pasajes, cierre de citas y suite de integridad."""
import json, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tesauro import TESAURO, AUTORIDADES, UMBRAL
from build import LINEAS, ALERTAS, CALENDARIO, API, STACK, FASES, ESTADO_META, \
                  JERARQUIA_META, FUERZA_META, ESQUEMA, PRUEBA

IDX = json.load(open("/tmp/pron/app/indice.json", encoding="utf-8"))
INT = json.load(open("/tmp/pron/app/integridad.json", encoding="utf-8"))

# el tesauro se envía plano al cliente, para búsqueda por sinónimo
TES = {m: {"frases": d.get("frases", []), "palabras": d.get("palabras", []),
           "normas": d.get("normas", [])} for m, d in TESAURO.items()}

FASES2 = [
  ("Fase 1", "Repositorio verificable", "Ingesta, texto congelado con hash, extracción de pasajes, verificación de citas y las 12 comprobaciones de integridad corriendo en cada carga.", "6–8 semanas"),
  ("Fase 2", "Recuperación multi-vía", "Tesauro con sinónimos, identidad canónica de autoridades, búsqueda por descriptor, texto lematizado, norma y grafo de citas, con convergencia declarada.", "5 semanas"),
  ("Fase 3", "Cierre de citas y vacíos", "Grafo completo, clasificación de referencias, calendario de vigencias y cola de adjudicación de divergencias.", "4 semanas"),
  ("Fase 4", "Dossier con certificado de alcance", "Exportación a Word: cronología, citas verificadas, mapa de concordancias y vacíos declarados. Nunca la conclusión.", "3 semanas"),
]

payload = {
 "docs": IDX["docs"], "pasajes": IDX["pasajes"], "citas": IDX["citas"],
 "vacios": IDX["vacios"], "integridad": INT, "tesauro": TES,
 "autoridades": AUTORIDADES, "umbral": UMBRAL,
 "lineas": LINEAS, "alertas": ALERTAS, "calendario": CALENDARIO,
 "api": API, "stack": STACK, "fases": FASES2, "prueba": PRUEBA,
 "estadoMeta": ESTADO_META, "jerarquiaMeta": JERARQUIA_META,
 "fuerzaMeta": FUERZA_META, "esquema": ESQUEMA,
}

CSS = open("/tmp/pron/app/estilo.css", encoding="utf-8").read()
JS  = open("/tmp/pron/app/app.js", encoding="utf-8").read()

HTML = """<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Repositorio de Criterios — Fiscalía CONAF · Prototipo v2</title>
<style>%s</style></head><body>

<header class="top"><div class="top-in">
  <div class="brandrow">
    <div class="brand">
      <div class="mark">FC</div>
      <div><h1>Repositorio de Criterios · Fiscalía</h1>
      <p>Corporación Nacional Forestal — biblioteca de criterio trazado</p></div>
    </div>
    <span class="protobadge" id="sello"></span>
  </div>
  <nav id="nav"></nav>
</div></header>

<main>
  <section class="view on" id="v-consulta"></section>
  <section class="view" id="v-lineas"></section>
  <section class="view" id="v-vacios"></section>
  <section class="view" id="v-corpus"></section>
  <section class="view" id="v-normas"></section>
  <section class="view" id="v-confianza"></section>
  <section class="view" id="v-arq"></section>
</main>

<div style="max-width:1180px;margin:0 auto;padding:0 28px 40px">
  <div class="foot">
    <span id="pie"></span>
    <span>Fiscalía · Corporación Nacional Forestal</span>
  </div>
</div>

<script>const D = %s;
%s</script>
</body></html>""" % (CSS, json.dumps(payload, ensure_ascii=False), JS)

with io.open("/tmp/pron/app/prototipo-fiscalia-v2.html", "w", encoding="utf-8") as f:
    f.write(HTML)
print("OK", os.path.getsize("/tmp/pron/app/prototipo-fiscalia-v2.html"), "bytes")
