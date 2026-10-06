# Pipeline — Operación Botín

Pipeline de datos para Operación Botín. Python 3.12 + [uv](https://docs.astral.sh/uv/).

## Módulos

- `src/models.py` — modelo `PostCapturado` (Pydantic) compartido por todos los extractores
- `src/extract/` — recolección de datos desde plataformas
  - `bluesky.py` — extractor de Bluesky (AT Protocol) ✅
  - `telegram.py` — extractor de Telegram (próximamente, Fase 1.3)
  - `twitter.py` — extractor de Twitter/X (próximamente, Fase 1.4)
- `src/storage.py` — guardado en Parquet + ficha de metadatos JSON
- `src/features/` — transformaciones y etiquetado (Fase 2)
- `src/rag/` — indexación semántica (Fase 3)

## Setup

    cd pipeline
    uv sync                 # instala dependencias en .venv
    uv sync --extra dev     # incluye ruff, mypy, pytest

## Configuración

Copia `.env.example` a `.env` (en la raíz del monorepo) y rellena credenciales:

    BLUESKY_HANDLE=tu-handle.bsky.social
    BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

> **Nunca** pegues credenciales en el chat ni las commitees. El `.env` está
> en `.gitignore`.

## Uso

### Extracción básica

    # Buscar 100 posts en Bluesky que mencionen "elecciones Colombia"
    uv run python -m src.extract --plataforma bluesky --termino "elecciones Colombia"

    # Con límite menor para pruebas
    uv run python -m src.extract --plataforma bluesky --termino "elecciones Colombia" --limite 20

    # Sin guardar en Parquet (solo ver resultados en consola)
    uv run python -m src.extract --plataforma bluesky --termino "elecciones Colombia" --no-guardar

### Salida

Los posts capturados se guardan en:

    packages/shared/data/raw/{plataforma}/{YYYY}/{MM}/{DD}/extraccion_{timestamp}.parquet
    packages/shared/data/raw/{plataforma}/{YYYY}/{MM}/{DD}/extraccion_{timestamp}.meta.json

Cada Parquet lleva su ficha `.meta.json` con fuente, fecha, método, total de
registros y errores. La ficha sigue la regla editorial §4: "todo dataset
lleva fuente atribuida".

## Modelo de datos

Cada post capturado cumple el esquema `PostCapturado` (ver `src/models.py`):

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_plataforma` | str | ID del post en la plataforma |
| `plataforma` | enum | bluesky, telegram, twitter, facebook, otra |
| `metodo_captura` | enum | api_oficial, scraping_publico, reporte_ciudadano, firehose |
| `autor_handle` | str | Handle público del autor |
| `autor_id_plataforma` | str | ID interno del autor (DID, user_id) |
| `texto` | str | Texto del post, sin recortes |
| `url` | str | URL pública del post |
| `fecha_publicacion` | datetime | UTC |
| `fecha_captura` | datetime | UTC, cuando capturamos |
| `termino_busqueda` | str? | Término que disparó la captura |
| `hash_contenido` | str | SHA-256 de texto+url, para detectar ediciones |
| `metadata` | dict | Campos extra específicos de plataforma |

## Calidad

    uv run ruff check src/        # lint
    uv run ruff format src/       # formatear
    uv run mypy src               # type check
    uv run pytest                 # tests (cuando existan)

## Estado

- ✅ **1.1** Credenciales configurables
- ✅ **1.2** Extractor Bluesky funcional
- ⏳ **1.3** Extractor Telegram (próximo)
- ⏳ **1.4** Extractor Twitter/X (próximo)
- ✅ **1.5** Modelo `PostCapturado`
- ✅ **1.6** Almacenamiento Parquet + ficha
- ✅ **1.7** CLI de extracción
- ✅ **1.8** Esta documentación

## Reglas editoriales aplicadas

- Solo se capturan **posts públicos**. Nunca mensajes privados ni DMs.
- Cada registro lleva `metodo_captura` para auditoría.
- `hash_contenido` permite detectar si un post fue editado después.
- Los identificadores de autor se conservan en crudo (`autor_handle`,
  `autor_id_plataforma`) pero **se seudonimizarán en la fase de features**
  antes de publicar.
- El pipeline respeta los rate-limits del SDK; no hace scraping agresivo.
