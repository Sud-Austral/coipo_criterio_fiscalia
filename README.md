<!-- AI:BEGIN id=readme sha=f582926a31b4 -->
# coipo_criterio_fiscalia

## Descripción

Proyecto relacionado con el manejo de criterios fiscales, documentos y normas. El código incluye procesamiento de textos, verificación de consistencia y construcción de índices.

## Stack técnico

- Python
- JavaScript
- SQL
- JSON
- HTML
- CSS
- YAML
- Markdown

## Estructura del proyecto

El proyecto contiene principalmente archivos en la carpeta `INSUMO/`, incluyendo:

- Código fuente en Python (`INSUMO/codigo/`)
- Documentación (`INSUMO/docs/`)
- Archivos de esquema de base de datos (`INSUMO/codigo/esquema.sql`)

## Base de datos

El esquema de base de datos incluye las siguientes tablas:

- organo
- documento
- criterio
- cita
- descriptor
- documento_descriptor
- norma
- criterio_norma
- relacion
- bitacora

## Desarrollo

El proyecto incluye scripts para:

- Verificación de integridad (`integridad.py`)
- Verificación de consistencia (`consistencia.py`)
- Construcción de índices (`indice.py`)
- Procesamiento de núcleo (`nucleo.py`)
- Manejo de tesauro (`tesauro.py`)
- Construcción de componentes (`build.py`, `build2.py`)

## Despliegue

El proyecto incluye configuración de despliegue en `.github/workflows/readme.yml`.
<!-- AI:END id=readme -->

<!-- ai-readme-fingerprint: sha256:2c053c29afa30096eecbcedc7c6a9762e4961da36475d5b02db98725b94d4964 -->
