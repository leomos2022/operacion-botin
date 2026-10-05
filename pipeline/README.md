# Pipeline — Operación Botín

Pipeline de datos para Operación Botín. Python 3.12 + [uv](https://docs.astral.sh/uv/).

## Módulos

- `src/extract/` — recolección de datos desde plataformas (Twitter, Telegram, Bluesky).
- `src/features/` — transformaciones, métricas y etiquetado.
- `src/rag/` — indexación semántica y retrieval.

## Setup

```bash
cd pipeline
uv sync                 # instala dependencias en .venv
uv run python -m src.extract    # placeholder
```

## Calidad

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest
```

## Estado

Fase 0.1 — solo scaffolding. Los módulos están vacíos a propósito; se
implementan en Fases 1–3 (ver `TASKS.md` en la raíz del monorepo).
