"""CLI del módulo de análisis de features.

Uso:
    uv run python -m src.features --analizar
"""

from __future__ import annotations

import click
from rich.console import Console
from rich.panel import Panel

from src.features.analisis import generar_hallazgos, guardar_hallazgos, mostrar_resumen

_console = Console()


@click.command()
@click.option(
    "--analizar",
    is_flag=True,
    default=True,
    help="Ejecutar análisis completo sobre el dataset Bluesky.",
)
def main(analizar: bool) -> None:
    """Ejecuta el análisis de features sobre los posts capturados."""
    _console.print(
        Panel.fit(
            "[bold]Operación Botín[/bold] — Análisis de features\n"
            "Detectando patrones temporales, de contenido y de grafo.",
            border_style="red",
        )
    )

    if not analizar:
        return

    hallazgos = generar_hallazgos()
    mostrar_resumen(hallazgos)
    guardar_hallazgos(hallazgos)

    _console.print("\n[bold green]✓ Análisis completo.[/bold green]")


if __name__ == "__main__":
    main()
