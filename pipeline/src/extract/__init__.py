"""Modulo de extraccion.

CLI:
    uv run python -m src.extract --plataforma bluesky --termino "elecciones Colombia"
    uv run python -m src.extract --plataforma telegram --canal @nombre_canal --limite 50
    uv run python -m src.extract --plataforma youtube --video-id VIDEO_ID --limite 100
"""

from .bluesky import ExtractorBluesky
from .telegram import ExtractorTelegram
from .youtube import ExtractorYouTube

__all__ = ["ExtractorBluesky", "ExtractorTelegram", "ExtractorYouTube"]
