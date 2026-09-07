# Solucion, leida del codigo

Advertencia previa, porque cambia como hay que leer todo lo que sigue: este
repositorio no tiene manifiestos de dependencias, ni endpoints, ni variables de
entorno. Todo lo ejecutable cuelga de una carpeta de insumos
[INSUMO/LEEME.md], y el analizador no extrajo el contenido de ningun archivo.
La evidencia disponible es el esquema de la base
[INSUMO/codigo/esquema.sql:19], los nombres de las funciones de siete programas
y la lista de archivos. Por eso este documento lleva mas marcas [PENDIENTE] de
lo que seria deseable, y eso mismo es informacion: dice hasta donde llega el
analizador.

## Que hace el sistema

Permite representar quien emite un pronunciamiento, que documento lo contiene,
que criterio sostiene ese documento y con que cita textual se respalda
[INSUMO/codigo/esquema.sql:19], [INSUMO/codigo/esquema.sql:25],
[INSUMO/codigo/esquema.sql:54], [INSUMO/codigo/esquema.sql:67]; permite
describir cada documento con descriptores de un vocabulario controlado
[INSUMO/codigo/esquema.sql:89], [INSUMO/codigo/esquema.sql:94],
[INSUMO/codigo/tesauro.py]; permite vincular un criterio con la norma que
interpreta [INSUMO/codigo/esquema.sql:100],
[INSUMO/codigo/esquema.sql:108]; permite registrar la relacion entre dos
criterios [INSUMO/codigo/esquema.sql:119]; y deja constancia de lo que ocurre
en una bitacora [INSUMO/codigo/esquema.sql:129]. [INFERIDO]

Del lado del procesamiento, permite tomar el texto de cada documento,
normalizarlo, recortar los pasajes y los parrafos relevantes, ubicar en que
pagina cae cada pasaje y calcular la huella del documento original
[INSUMO/codigo/nucleo.py]; construir a partir de eso un indice consultable, con
las materias y las normas de cada entrada, marcando cual es el pasaje principal
[INSUMO/codigo/indice.py]; y comprobar despues que lo construido es consistente
e integro [INSUMO/codigo/consistencia.py], [INSUMO/codigo/integridad.py]. El
resultado se muestra en una pagina de prototipo
[INSUMO/prototipo/prototipo-fiscalia-v2.html], [INSUMO/codigo/app.js],
[INSUMO/codigo/estilo.css]. [INFERIDO]

## Roles: quien ve que

- No hay roles en el codigo. No se detecto ningun endpoint ni ninguna variable
  de entorno en todo el repositorio; los programas operan sobre archivos
  [INSUMO/codigo/build.py], [INSUMO/codigo/dataset.py]. [INFERIDO]
- El esquema concede permisos a un perfil publico de base de datos
  [INSUMO/codigo/esquema.sql:139]. Que eso sea intencional: [VERIFICAR]
- Quien puede consultar y quien puede alimentar el sistema: [PENDIENTE]

## De donde salen los datos

- La fuente es un conjunto de veinte pronunciamientos convertidos a texto
  plano y guardados uno por archivo bajo la carpeta de texto extraido, que el
  codigo carga en bloque [INSUMO/codigo/nucleo.py]. Los nombres de esos
  archivos identifican el organo emisor y el numero del acto; no se transcriben
  aca. Quien es dueno de ese acervo y quien autoriza su uso: [PENDIENTE]
  [VERIFICAR] [INFERIDO]
- El repositorio conserva los productos derivados de ese procesamiento como
  archivos de datos: el indice [INSUMO/datos/indice.json], el resultado de la
  comprobacion de consistencia [INSUMO/datos/consistencia.json], el de
  integridad [INSUMO/datos/integridad.json] y el de verificacion
  [INSUMO/datos/verificacion.json]. Son salidas de los programas, no fuentes.
  [INFERIDO]
- El vocabulario controlado tiene su propia definicion
  [INSUMO/codigo/tesauro.py] y su documento [INSUMO/docs/05-TESAURO-Y-VOCABULARIO.md].
  Quien es dueno de ese vocabulario y quien lo aprueba: [PENDIENTE]

## Reglas que el sistema impone por si mismo

- La comprobacion de integridad esta escrita como quince verificaciones
  numeradas e independientes, ejecutadas en conjunto
  [INSUMO/codigo/integridad.py], con su resultado persistido
  [INSUMO/datos/integridad.json]. Que comprueba cada una: [PENDIENTE]
- Hay una comprobacion de consistencia aparte
  [INSUMO/codigo/consistencia.py], cuyo resultado se carga dentro de la de
  integridad [INSUMO/codigo/integridad.py]. Es decir, una depende de la otra.
  [INFERIDO]
- Las reglas de calidad estan escritas en un documento propio
  [INSUMO/docs/03-REGLAS-DE-CALIDAD.md]. Su contenido no fue extraido:
  [PENDIENTE]
- La identificacion de cada pronunciamiento se canoniza en una funcion unica
  [INSUMO/codigo/nucleo.py], de modo que la misma referencia escrita de dos
  maneras se resuelva igual. [INFERIDO]
- Cada documento se sella con una huella calculada sobre el archivo original
  [INSUMO/codigo/nucleo.py], lo que permite detectar si el texto extraido
  dejo de corresponder a su fuente. [INFERIDO]

## Que NO hace

Solo ausencias que el analizador enumero de forma exhaustiva.

- No hay servicio: no se detecto ningun endpoint ni ningun manifiesto de
  dependencias en todo el repositorio. Lo que hay es un conjunto de programas
  que se ejecutan sobre archivos [INSUMO/codigo/build.py],
  [INSUMO/codigo/build2.py] y una pagina que se abre en el navegador
  [INSUMO/prototipo/prototipo-fiscalia-v2.html]. [INFERIDO]
- No hay ninguna variable de entorno: la configuracion, si existe, esta escrita
  dentro de los propios programas [INSUMO/codigo/dataset.py]. [INFERIDO]
- El esquema de base existe [INSUMO/codigo/esquema.sql:25] pero nada en la
  evidencia muestra que se este usando: los datos que el repositorio conserva
  estan en archivos [INSUMO/datos/indice.json], no en una base. Es decir, el
  esquema esta escrito y no consta que este poblado. [INFERIDO]

## Iteraciones

- Hay dos generaciones del programa constructor conviviendo
  [INSUMO/codigo/build.py] y [INSUMO/codigo/build2.py], donde el segundo
  importa al primero. Cual esta vigente: [PENDIENTE] [INFERIDO]
- La documentacion esta numerada de principio a fin, de un resumen ejecutivo
  [INSUMO/docs/00-RESUMEN-EJECUTIVO.md] a una bitacora de defectos
  [INSUMO/docs/08-BITACORA-DE-DEFECTOS.md], pasando por la especificacion
  funcional [INSUMO/docs/01-ESPECIFICACION-FUNCIONAL.md], el modelo de datos
  [INSUMO/docs/02-MODELO-DE-DATOS.md], las reglas de calidad
  [INSUMO/docs/03-REGLAS-DE-CALIDAD.md], la ingesta
  [INSUMO/docs/04-CANALIZACION-DE-INGESTA.md], el vocabulario
  [INSUMO/docs/05-TESAURO-Y-VOCABULARIO.md], el plan
  [INSUMO/docs/06-PLAN-DE-IMPLEMENTACION.md] y los hallazgos del conjunto
  [INSUMO/docs/07-HALLAZGOS-DEL-CORPUS.md]. Esa numeracion es una secuencia de
  trabajo, no necesariamente el orden en que se escribio. [INFERIDO]
- El prototipo lleva version en el nombre
  [INSUMO/prototipo/prototipo-fiscalia-v2.html], lo que implica que hubo uno
  anterior que no esta en el repositorio. [INFERIDO]
- Que este repositorio se llame insumo y no producto es coherente con que todo
  cuelgue de esa carpeta [INSUMO/LEEME.md]: se lee como material previo a un
  desarrollo, no como el desarrollo. Confirmarlo: [PENDIENTE] [INFERIDO]

## Donde el analizador no ve

Esta es la parte util de este documento.

- No se extrajo el contenido de ninguno de los veinte documentos del conjunto
  de texto extraido. Todo lo que este documento dice sobre ellos sale de la
  estructura del codigo que los procesa [INSUMO/codigo/nucleo.py], no de lo que
  dicen. Sus rutas tampoco se transcriben aca porque incluyen numeros de actos y
  de normas: [VERIFICAR]
- No se extrajo el contenido de ninguno de los nueve documentos de
  especificacion [INSUMO/docs/01-ESPECIFICACION-FUNCIONAL.md],
  [INSUMO/docs/02-MODELO-DE-DATOS.md]. Son justamente los que responderian casi
  todo lo marcado [PENDIENTE] aca.
- No se extrajeron los archivos de datos derivados
  [INSUMO/datos/indice.json], [INSUMO/datos/verificacion.json]: no se sabe
  cuantas entradas tienen ni si las comprobaciones pasaron.
- La pagina de prototipo declara vistas y vias de navegacion
  [INSUMO/codigo/app.js] que el analizador no enumero. Que pantallas ofrece:
  [PENDIENTE]
- El archivo que explica el conjunto [INSUMO/LEEME.md] no fue leido.
