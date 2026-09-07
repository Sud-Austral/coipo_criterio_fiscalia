# Problema, reconstruido desde el codigo

Nadie del area usuaria participo. Se deduce el problema desde lo construido, y
cada paso va marcado. Advertencia previa: todo lo que hay en este repositorio
cuelga de una sola carpeta de insumos [INSUMO/LEEME.md], y el analizador no
extrajo el contenido de ningun archivo. Lo que sigue se apoya en el esquema de
datos, en los nombres de las funciones y en la estructura de carpetas.

## Que se deduce que estaba roto

- El modelo de datos separa el documento de su contenido interpretado: hay una
  entidad para el organo que emite [INSUMO/codigo/esquema.sql:19], otra para el
  documento [INSUMO/codigo/esquema.sql:25], otra para el criterio que ese
  documento sostiene [INSUMO/codigo/esquema.sql:54] y otra para la cita textual
  que respalda el criterio [INSUMO/codigo/esquema.sql:67]. Luego probablemente
  habia un problema con saber que criterio se sostuvo, quien lo sostuvo y en
  que parte del texto consta. [INFERIDO]
- Hay una entidad de relacion entre criterios [INSUMO/codigo/esquema.sql:119].
  Luego probablemente un criterio podia confirmar, matizar o contradecir a otro
  y eso no estaba registrado en ninguna parte. [INFERIDO]
- Hay una entidad de norma y un cruce entre criterio y norma
  [INSUMO/codigo/esquema.sql:100], [INSUMO/codigo/esquema.sql:108]. Luego
  probablemente costaba responder que se ha dicho sobre una disposicion
  determinada. [VERIFICAR] toda afirmacion sobre normas concretas: no es este
  documento el que la cierra.
- Hay un vocabulario controlado con termino preferido
  [INSUMO/codigo/tesauro.py] y entidades de descriptor y su cruce con el
  documento [INSUMO/codigo/esquema.sql:89],
  [INSUMO/codigo/esquema.sql:94], mas un documento que lo explica
  [INSUMO/docs/05-TESAURO-Y-VOCABULARIO.md]. Luego probablemente el mismo
  asunto se nombraba de varias maneras distintas segun quien buscara.
  [INFERIDO]
- El texto de los documentos se procesa: se normaliza, se pliega, se recortan
  pasajes y parrafos y se calcula la pagina en que cae cada uno
  [INSUMO/codigo/nucleo.py]. Luego probablemente el punto de partida eran
  documentos en formato portatil sobre los que no se podia buscar de forma
  util. [INFERIDO]
- El problema de negocio concreto, con quien lo planteo: [PENDIENTE]

## Quien sufre el problema

- El codigo no impone ningun rol: no se detecto ningun endpoint, ninguna
  variable de entorno ni ningun manifiesto de dependencias en todo el
  repositorio. Lo unico ejecutable son programas que operan sobre archivos
  [INSUMO/codigo/build.py], [INSUMO/codigo/indice.py] y una pagina de
  prototipo [INSUMO/prototipo/prototipo-fiscalia-v2.html]. [INFERIDO]
- Hay una entidad de bitacora en el esquema
  [INSUMO/codigo/esquema.sql:129] y una concesion de permisos a un perfil
  publico [INSUMO/codigo/esquema.sql:139]. Que esa concesion sea intencional y
  a quien alcanza: [PENDIENTE] [INFERIDO]
- Quien consultaria esto y quien lo alimentaria: [PENDIENTE]
- Cuantas personas: [PENDIENTE]

## Como lo resolvian antes

- El insumo son documentos en formato portatil convertidos a texto plano,
  guardados uno por documento en una carpeta de texto extraido
  [INSUMO/codigo/nucleo.py], y el codigo calcula la huella del documento
  original y las posiciones de sus paginas
  [INSUMO/codigo/nucleo.py]. Que exista un paso de extraccion sugiere que la
  fuente eran los documentos sueltos, y que la busqueda se hacia abriendolos.
  [INFERIDO]
- Hay un documento que describe la canalizacion de ingesta
  [INSUMO/docs/04-CANALIZACION-DE-INGESTA.md]. Su contenido no fue extraido:
  [PENDIENTE]
- Quien reunia esos documentos y cuanto tardaba en encontrar un criterio
  anterior: [PENDIENTE]

## Volumen

- Indicios, no cifras. La carpeta de texto extraido contiene veinte archivos
  numerados correlativamente, y el propio repositorio dedica un documento a los
  hallazgos de ese conjunto [INSUMO/docs/07-HALLAZGOS-DEL-CORPUS.md]. Veinte
  documentos es un conjunto de partida, no un archivo historico: si esa es la
  escala definitiva o solo la de la prueba, [PENDIENTE]. [INFERIDO]
- Hay quince comprobaciones de integridad escritas una por una
  [INSUMO/codigo/integridad.py]. Que se hayan escrito quince sugiere que los
  datos se contradecian de varias maneras distintas. Es un indicio de calidad,
  no de tamano. [INFERIDO]
- Cuantos documentos hay en total en el acervo del que salieron estos:
  [PENDIENTE]

## Que pasa si no se hace nada

[PENDIENTE], sin excepcion. El codigo no lo responde y no se deduce de que el
repositorio exista.

## Quien decide que esta terminado

[PENDIENTE], sin excepcion. Hay un plan de implementacion escrito
[INSUMO/docs/06-PLAN-DE-IMPLEMENTACION.md] y una bitacora de defectos
[INSUMO/docs/08-BITACORA-DE-DEFECTOS.md], pero ninguno nombra a la persona o la
instancia que acepta el trabajo. [INFERIDO]

## Materia juridica y datos personales

- Todo el objeto de este repositorio es material de pronunciamiento juridico
  interno: el modelo guarda organos, documentos, criterios y normas
  [INSUMO/codigo/esquema.sql:19], [INSUMO/codigo/esquema.sql:25],
  [INSUMO/codigo/esquema.sql:54], [INSUMO/codigo/esquema.sql:100]. Ninguna
  afirmacion sobre el contenido de esos pronunciamientos, sobre las normas que
  citan ni sobre su vigencia se hace en este documento: [VERIFICAR]
- Varios nombres de archivo de la carpeta de texto extraido mencionan
  pronunciamientos sobre proteccion de datos personales y sobre transparencia.
  No se transcriben aca. Si esos textos contienen datos de personas
  identificables: [VERIFICAR]
- La evidencia del repositorio lo marca como no privado, y su contenido es
  material interno de pronunciamiento. [VERIFICAR] si corresponde que sea de
  acceso publico.
- El esquema concede permisos a un perfil publico de base de datos
  [INSUMO/codigo/esquema.sql:139]. [VERIFICAR]
