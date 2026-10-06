"""Módulo de features y etiquetado.

Transformaciones, métricas agregadas y etiquetado de cuentas según
criterios definidos en /metodología (bot, troll, cuenta falsa,
operador coordinado).

CLI:
    uv run python -m src.features --analizar
"""

from .analisis import generar_hallazgos, guardar_hallazgos
from .seudonimizacion import seudonimizar

__all__ = ["generar_hallazgos", "guardar_hallazgos", "seudonimizar"]
