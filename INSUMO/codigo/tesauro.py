# -*- coding: utf-8 -*-
"""
Tesauro de materias, con fuerza de evidencia.

  frases   → expresiones de varias palabras, propias de la materia. Peso 2:
             bastan por sí solas para etiquetar.
  palabras → términos de una palabra, distintivos pero ambiguos fuera de
             contexto. Peso 1: se exigen DOS coincidencias distintas.

El umbral de 2 es lo que impide que «superficie» dispare «Cabida predial» en
un texto sobre monumentos naturales, o que «conservación» dispare «Protección
de datos» en uno sobre recursos forestales. Ambos fallos ocurrieron y esta es
la corrección.
"""

TESAURO = {
 "Monumentos naturales": {
   "frases": ["monumento natural","monumentos naturales","belloto del norte",
              "belloto del sur","origen antrópico","protección absoluta",
              "especie protegida","especies protegidas","medio ambiente natural",
              "intervención humana"],
   "palabras": ["araucaria","araucana","belloto","queule","pitao","ruil",
                "inviolabilidad","descepado","plantada","plantados"],
   "normas": ["DS 13/1995","DS 43/1990","Ley 20.283 art. 19"]},

 "Áreas silvestres protegidas": {
   "frases": ["parque nacional","parques nacionales","área protegida","áreas protegidas",
              "reserva nacional","plan de manejo de la unidad","fauna silvestre",
              "perros asilvestrados","patrimonio natural","diversidad biológica"],
   "palabras": ["conguillío","asilvestrados","snaspe","smart"],
   "normas": ["Ley 21.600","Ley 19.300 art. 34"]},

 "Planes de manejo": {
   "frases": ["plan de manejo","planes de manejo","estudio técnico",
              "criterios de admisibilidad","documentación legal","tipo de interesado",
              "plan de manejo de plantaciones"],
   "palabras": ["admisibilidad","interesado","servidumbre","concesión"],
   "normas": ["Ley 20.283","DS 93/2008 art. 22","Ley 21.770"]},

 "Cabida predial": {
   "frases": ["superficie predial","diferencia de cabida","diferencias de cabida",
              "cuerpo cierto","título de dominio","títulos de dominio",
              "conservador de bienes raíces","anotaciones marginales",
              "margen de tolerancia","márgenes de tolerancia","avalúo fiscal",
              "carpeta predial","predio rústico"],
   "palabras": ["cabida","deslindes","traslape","traslapes","subdivisión"],
   "normas": ["Código Civil art. 1831","Código Civil art. 1832"]},

 "Reforestación y compensación": {
   "frases": ["medida de compensación","medidas de compensación","compensación ambiental",
              "vida útil","pérdida neta cero","efecto positivo alternativo",
              "obligación de reforestar","fin ambiental"],
   "palabras": ["reforestación","reforestar","prendimiento","sobrevivencia","equivalencia"],
   "normas": ["DS 40/2012 art. 100","Ley 20.283 art. 14","Ley 20.283 art. 21"]},

 "SEIA / RCA / PAS": {
   "frases": ["permiso ambiental sectorial","permisos ambientales sectoriales",
              "resolución de calificación ambiental","evaluación de impacto ambiental"],
   "palabras": ["seia","rca","pas","sma"],
   "normas": ["DS 40/2012","Ley 19.300"]},

 "Fiscalización forestal": {
   "frases": ["ministro de fe","ministros de fe","juzgado de policía local",
              "presunción de veracidad","acciones de fiscalización",
              "labor fiscalizadora","potestad pública"],
   "palabras": ["fiscalizador","fiscalizadores","infraccional",
                "externalizar","externalización"],
   "normas": ["Ley 20.283 art. 47","DL 701 art. 24","DS 93/2008 art. 45"]},

 "Contratación pública": {
   "frases": ["bases de licitación","bases administrativas","licitación pública",
              "sujeción a las bases","convenio marco","precio contractual",
              "contrato garantizado","suma alzada","trato directo","orden de compra",
              "comisión evaluadora","oferta económica","cláusula de reajuste",
              "compras públicas","combustible aeronáutico"],
   "palabras": ["oferente","oferentes","adjudicación","adjudicatario","licitar","adjudicar",
                "reajuste","cotización"],
   "normas": ["Ley 19.886","DS 250/2004","Ley 21.634"]},

 "Probidad y conflictos de interés": {
   "frases": ["conflicto de interés","conflictos de interés","grado de consanguinidad",
              "35 quáter","35 sexies","prohibición establecida",
              "vínculo de parentesco","jefatura superior",
              "escasez objetiva"],
   "palabras": ["parentesco","consanguinidad","afinidad","inhabilidad"],
   "normas": ["Ley 19.886 art. 35 quáter","Ley 19.886 art. 35 sexies","Ley 20.880"]},

 "Protección de datos personales": {
   "frases": ["datos personales","dato personal","datos sensibles","protección de datos",
              "vida privada","base de licitud",
              "consentimiento expreso","principio de finalidad","datos biométricos",
              "evaluación de impacto en protección","protección desde el diseño",
              "titular de los datos","números telefónicos","delegado de protección",
              "plazo de conservación","plazos de conservación","fuentes accesibles"],
   "palabras": ["geolocalización","seudonimización","anonimización","biométricos",
                "intimidad","tarjado","tarjar","tarjaron"],
   "normas": ["Ley 19.628","Ley 21.719","CPR art. 19 N°4"]},

 "Transparencia y acceso a la información": {
   "frases": ["acceso a la información","persona jurídica","personas jurídicas","causal de reserva","causales de secreto","derecho de acceso"],
   "palabras": ["amparo","reclamante","requirente"],
   "normas": ["Ley 20.285","CPR art. 8"]},

 "Actos administrativos": {
   "frases": ["acto administrativo","actos administrativos","resolución fundada",
              "resoluciones fundadas","presunción de legalidad","convenio de colaboración",
              "convenios de colaboración","sanción administrativa","acto aprobatorio",
              "declaraciones de voluntad"],
   "palabras": ["formalización","regularización","aprobatorio"],
   "normas": ["Ley 19.880 art. 3"]},

 "Procedimiento administrativo": {
   "frases": ["procedimiento administrativo",
              "recurso de reconsideración","recurso jerárquico","principio conclusivo",
              "principio de celeridad","no son fatales","antecedentes complementarios",
              "orden del superior"],
   "palabras": ["celeridad","fatales","reconsideración","representarla"],
   "normas": ["Ley 19.880","Ley 18.575","DFL 29 art. 62"]},

 "Naturaleza jurídica de CONAF": {
   "frases": ["corporación de derecho privado","derecho privado","potestades públicas",
              "función administrativa","órganos y servicios públicos",
              "necesidades de la comunidad"],
   "palabras": ["sernafor"],
   "normas": ["Ley 21.744","Ley 18.575"]},

 "Gestión de personas": {
   "frases": ["trabajo a distancia","horas extraordinarias","trabajo extraordinario",
              "jornada laboral","jornadas presenciales","vivienda fiscal","viviendas fiscales",
              "organizaciones sindicales","labores de cuidado","cuidado no remunerado","relación laboral"],
   "palabras": ["teletrabajo","presencialidad","comodato","cuidadoras",
                "sindicato","sindicatos","sindical","sindicales"],
   "normas": ["Código del Trabajo","DL 249/1974","Ley 21.645","DFL 29 art. 91"]},

 "Remuneraciones": {
   "frases": ["asignación de estímulo","función directiva","remuneración bruta",
              "fijación de remuneraciones","estímulo al desempeño","sueldo base"],
   "palabras": ["imponible","emolumento","emolumentos","dieta"],
   "normas": ["Ley 20.300","CPR art. 38 bis","Ley 21.233"]},

 "Límites de competencia": {
   "frases": ["excede sus facultades","no está facultada","sentencia judicial","dentro de su competencia",
              "no tendrán más atribuciones","costumbre no constituye derecho"],
   "palabras": ["sag","incompetencia"],
   "normas": ["Ley 18.575 art. 2","CPR art. 6","CPR art. 7"]},

 "Bienes institucionales": {
   "frases": ["vivienda fiscal","viviendas fiscales","acta de recepción","inventario detallado",
              "consumos básicos","silvicultura preventiva","restitución del inmueble",
              "uso y restitución"],
   "palabras": ["comodato","habitabilidad","ocupante","viviendas","restitución"],
   "normas": ["DFL 29 art. 91"]},
}

PESO_FRASE, PESO_PALABRA, UMBRAL = 2, 1, 2

# ── Identidad canónica de autoridades externas ────────────────────────
AUTORIDADES = {
 "CGR-33624":  {"nombre":"Dictamen CGR E33624/2020","variantes":["E33624","33624","33.624","E33624N20"],
   "doctrina":"CONAF se enmarca en el concepto de órganos y servicios públicos creados para el cumplimiento de la función administrativa.","clave":True},
 "CGR-337332": {"nombre":"Dictamen CGR E337332/2023","variantes":["E337332","E337332N23"],
   "doctrina":"Los plazos de la Administración no son fatales, pero rigen los principios de celeridad y conclusivo.","clave":False},
 "CGR-125384": {"nombre":"Dictamen CGR E125384/2021","variantes":["E125384"],"doctrina":"","clave":False},
 "CGR-284318": {"nombre":"Dictamen CGR E284318/2022","variantes":["E284318"],"doctrina":"","clave":False},
 "CGR-149544": {"nombre":"Dictamen CGR E149544/2025","variantes":["E149544"],
   "doctrina":"Estricta sujeción a las bases, en la etapa licitatoria y en la ejecución del contrato.","clave":True},
 "CGR-69939":  {"nombre":"Oficio CGR E69939/2025","variantes":["E69939"],
   "doctrina":"El art. 35 quáter es preventivo, amplio y objetivo; opera respecto de todo el organismo.","clave":True},
 "CGR-389863": {"nombre":"Dictamen CGR E389863/2023","variantes":["E389863"],
   "doctrina":"La declaración de monumento natural no alcanza a los individuos producto de intervención humana.","clave":True},
 "CGR-443357": {"nombre":"Dictamen CGR 443357/2024","variantes":["443357"],
   "doctrina":"Exige al menos tres jornadas diarias presenciales dentro de la jornada semanal.","clave":True},
 "CGR-263":    {"nombre":"Dictamen CGR D263/2026","variantes":["263","D263"],
   "doctrina":"Reconsidera la jurisprudencia sobre viviendas fiscales; 60 días hábiles para dictar normativa interna.","clave":True},
 "CGR-9527":   {"nombre":"Dictamen CGR 9.527/2013","variantes":["9527","9.527"],
   "doctrina":"Improcedente externalizar la función de inspección.","clave":False},
 "CGR-12528":  {"nombre":"Dictamen CGR 12.528/1996","variantes":["12528","12.528"],
   "doctrina":"Las tareas inherentes a la función pública no se encomiendan a terceros.","clave":False},
 "CGR-1084":   {"nombre":"Dictamen DT 1084/013 (2012)","variantes":["1084"],
   "doctrina":"Régimen del personal de CONAF: DL 249 con Código del Trabajo supletorio.","clave":False},
 "CGR-1949":   {"nombre":"Dictamen DT 1949/032 (2021)","variantes":["1949"],
   "doctrina":"Aplicación de la Ley 21.220 de trabajo a distancia al personal de CONAF.","clave":False},
 "CGR-67":     {"nombre":"Dictamen DT 67/01 (2024)","variantes":["67"],
   "doctrina":"Beneficiarios de la Ley 21.645 de conciliación.","clave":False},
 "CGR-591":    {"nombre":"Resolución CONAF 591/2020","variantes":["591"],
   "doctrina":"Oficializa la Guía de Evaluación Ambiental.","clave":True},
}


# ── Vocabulario único ────────────────────────────────────────────────
# Los descriptores curados a mano usaban nombres que no eran términos
# preferidos del tesauro («Jornada y teletrabajo», «Ley 20.283»). Dos
# vocabularios para lo mismo es una inconsistencia estructural: la búsqueda
# por materia nunca calza con lo que un abogado escribió en la ficha.
# Aquí se declara la equivalencia, y la verificación V13 comprueba que NINGÚN
# descriptor quede fuera del tesauro.
EQUIVALENTES = {
 "Jornada y teletrabajo":        "Gestión de personas",
 "Ley 20.283":                   "Planes de manejo",
 "Datos sensibles":              "Protección de datos personales",
 "Principio de finalidad":       "Protección de datos personales",
 "Estricta sujeción a las bases":"Contratación pública",
 "Servicios aéreos":             "Contratación pública",
 "Función pública indelegable":  "Fiscalización forestal",
 "Fiscalización ambiental":      "SEIA / RCA / PAS",
 "Convenios":                    "Actos administrativos",
 "Plazos":                       "Procedimiento administrativo",
 "Principio conclusivo":         "Procedimiento administrativo",
 "Reporte presupuestario":       "Límites de competencia",
}

def preferido(descriptor):
    """Descriptor curado → término preferido del tesauro."""
    if descriptor in TESAURO: return descriptor
    return EQUIVALENTES.get(descriptor, descriptor)
