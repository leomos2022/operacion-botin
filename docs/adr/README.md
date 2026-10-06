# Architecture Decision Records (ADRs)

Este directorio contiene las decisiones arquitectónicas significativas del proyecto **Operación Botín**. Cada ADR documenta el contexto, la decisión, sus consecuencias y alternativas consideradas.

## Formato

Cada ADR sigue una versión simplificada del formato MADR:

- **Estado**: Propuesto | Aceptado | Reemplazado | Deprecado
- **Fecha**: ISO 8601
- **Contexto**: qué problema resuelve
- **Decisión**: qué decidimos
- **Consecuencias**: qué implica
- **Alternativas**: qué más se consideró

## Convenciones de nombrado

`NNNN-titulo-corto.md` donde `NNNN` es un número secuencial de 4 dígitos, empezando en `0001`.

## Índice

| N° | Título | Estado |
|----|--------|--------|
| [0001](./0001-seleccion-de-stack.md) | Selección de stack: Astro + Cloudflare + Python | Aceptado |
| [0002](./0002-categorizacion-de-bots.md) | Categorización de cuentas: 4 categorías técnicas | Aceptado |
| [0003](./0003-modelo-freemium.md) | Modelo freemium de 3 capas para monetización | Aceptado |

## Cuándo añadir un ADR

Añade un ADR cuando tomes una decisión que:
- Afecte la arquitectura del sistema (stack, patrones, dependencias clave)
- Defina reglas editoriales o de negocio no obvias
- Tenga consecuencias a largo plazo difícilmente reversibles
- Resuelva una tensión entre alternativas razonables

No añadas un ADR para decisiones triviales (color de botón, nombre de variable). El ADR existe para que dentro de un año alguien pueda entender **por qué** se decidió algo, no solo **qué** se decidió.
