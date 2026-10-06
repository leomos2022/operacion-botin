"""Seudonimización de identificadores de cuenta.

Regla editorial §4.4:
"No doxxing. Mostrar identificadores seudonimizados (p. ej. @cuenta***01)
salvo cuando la cuenta haya sido identificada públicamente por una autoridad
o investigación periodística firmada."

Este módulo toma un handle público y devuelve su versión seudonimizada.
La asignación es determinística (mismo handle -> mismo seudónimo) gracias
a un hash del handle.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Seudonimo:
    """Asignación seudonimizada de un handle público."""

    seudonimo: str  # p. ej. "@cuenta***03"
    indice: int  # 3 en el ejemplo de arriba


# Handles que NO se seudonimizan: medios tradicionales reconocidos,
# cuentas verificadas públicamente, autoridades.
# Esta lista se mantiene conservadora: añadir solo si hay evidencia
# pública clara de que la cuenta es un medio o institución oficial.
HANDLES_PUBLICOS_PERMITIDOS: set[str] = {
    # Medios tradicionales colombianos
    "elespectador.com",
    "eltiempo.com",
    "semana.com",
    "lacolumna.com",
    # Agencias internacionales
    "reuters.com",
    "apnews.com",
    "bbc.com",
    # Observatorios y organizaciones
    "factcheckingcolombia.com",
}


def seudonimizar(handle: str) -> Seudonimo:
    """Devuelve un seudónimo determinístico para el handle.

    Si el handle está en la lista de permitidos públicos, se devuelve
    sin seudonimizar (indicado por indice=-1).

    Args:
        handle: handle público de Bluesky (p. ej. "lagaceta.bsky.social")

    Returns:
        Seudonimo con el seudónimo y su índice.
    """
    if handle in HANDLES_PUBLICOS_PERMITIDOS:
        return Seudonimo(seudonimo=f"@{handle}", indice=-1)

    # Hash determinístico del handle -> número entre 01 y 99
    h = hashlib.sha256(handle.encode("utf-8")).hexdigest()
    indice = int(h[:8], 16) % 99 + 1  # 1..99

    return Seudonimo(seudonimo=f"@cuenta***{indice:02d}", indice=indice)


def es_publico_permitido(handle: str) -> bool:
    """True si el handle es de un medio/autoridad pública reconocida."""
    return handle in HANDLES_PUBLICOS_PERMITIDOS
