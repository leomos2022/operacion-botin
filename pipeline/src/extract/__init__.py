"""Módulo de extracción.

CLI:
    uv run python -m src.extract --plataforma bluesky --termino "elecciones Colombia"
    uv run python -m src.extract --plataforma telegram --canal @nombre_canal --limite 50
"""

from .bluesky import ExtractorBluesky
from .telegram import ExtractorTelegram

__all__ = ["ExtractorBluesky", "ExtractorTelegram"]
