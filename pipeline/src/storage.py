"""Almacenamiento de posts capturados.

Guarda los posts en formato Parquet particionado por fecha de captura,
dentro de `packages/shared/data/raw/`. Cada archivo Parquet lleva
asociado un JSON de metadatos (ficha) con la fuente, fecha, cantidad de
registros y método de captura.

Reglas editoriales (AGENT_RULES.md §4):
- Todo dataset lleva una ficha (.meta.json) con fuente, fecha, método.
- Los Parquet se ignoran en git (.gitignore); los JSON sí se versionan.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from rich.console import Console

from src.models import Plataforma, ResultadoExtraccion

_console = Console()

# Raíz del monorepo (4 niveles arriba de este archivo: src/storage.py → src → pipeline → monorepo)
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_DIR = _REPO_ROOT / "packages" / "shared" / "data" / "raw"


def guardar_extraccion(resultado: ResultadoExtraccion) -> tuple[Path, Path]:
    """Guarda el resultado de una extracción en Parquet + JSON meta.

    Args:
        resultado: resultado de la extracción con los posts capturados.

    Returns:
        Tupla (ruta_parquet, ruta_meta_json).
    """
    fecha = resultado.fecha_fin
    subdirs = (
        _DATA_DIR
        / resultado.plataforma.value
        / str(fecha.year)
        / f"{fecha.month:02d}"
        / f"{fecha.day:02d}"
    )
    subdirs.mkdir(parents=True, exist_ok=True)

    ts = fecha.strftime("%Y%m%d_%H%M%S")
    parquet_path = subdirs / f"extraccion_{ts}.parquet"
    meta_path = subdirs / f"extraccion_{ts}.meta.json"

    records = [_post_to_dict(p) for p in resultado.posts] if resultado.posts else []
    df = pd.DataFrame(records)

    df.to_parquet(parquet_path, index=False, engine="pyarrow")

    meta = _build_meta(resultado, parquet_path, df)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    _console.print(
        f"[green]✓[/green] Guardados {len(resultado.posts)} posts en:\n"
        f"   Parquet: [bold]{parquet_path.relative_to(_REPO_ROOT)}[/bold]\n"
        f"   Ficha:   [bold]{meta_path.relative_to(_REPO_ROOT)}[/bold]"
    )

    return parquet_path, meta_path


def _post_to_dict(post: Any) -> dict[str, Any]:
    """Convierte un PostCapturado a dict plano para DataFrame."""
    d = post.model_dump(mode="json")
    d["metadata_json"] = json.dumps(d.pop("metadata", {}), ensure_ascii=False)
    return d


def _build_meta(
    resultado: ResultadoExtraccion,
    parquet_path: Path,
    df: pd.DataFrame,
) -> dict[str, Any]:
    """Construye la ficha de metadatos (.meta.json) del dataset."""
    return {
        "fuente": {
            "plataforma": resultado.plataforma.value,
            "metodo_captura": resultado.posts[0].metodo_captura.value
            if resultado.posts
            else None,
            "termino_busqueda": resultado.termino_busqueda,
            "url_api": "https://bsky.social/api" if resultado.plataforma == Plataforma.BLUESKY else None,
        },
        "fecha_captura_inicio": resultado.fecha_inicio.isoformat(),
        "fecha_captura_fin": resultado.fecha_fin.isoformat(),
        "duracion_segundos": resultado.duracion_segundos,
        "total_registros": len(resultado.posts),
        "errores": resultado.errores,
        "esquema": {
            "id": "PostCapturado v0.1",
            "campos_principales": list(df.columns) if not df.empty else [],
        },
        "archivo_parquet": str(parquet_path.relative_to(_REPO_ROOT)),
        "responsable": "pipeline v0.1",
        "fecha_creacion_ficha": datetime.now(UTC).isoformat(),
        "notas": (
            "Dataset crudo de extracción. Los identificadores de autor se "
            "seudonimizarán en la fase de features."
        ),
    }
