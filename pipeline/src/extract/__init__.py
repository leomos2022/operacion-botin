"""Módulo de extracción.

Recolección de datos desde plataformas sociales (Twitter/X, Telegram,
Bluesky) con rate-limit estricto y registro de fuente de cada registro.

CLI:
    uv run python -m src.extract --plataforma bluesky --termino "elecciones Colombia"
"""

from .bluesky import ExtractorBluesky

__all__ = ["ExtractorBluesky"]
