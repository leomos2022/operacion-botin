"""CLI del pipeline de extraccion de Operacion Botin.

Uso:
    uv run python -m src.extract --plataforma bluesky --termino "elecciones Colombia"
    uv run python -m src.extract --plataforma telegram --canal @nombre_canal --limite 50
    uv run python -m src.extract --plataforma youtube --video-id VIDEO_ID --limite 100
"""

from __future__ import annotations

import sys
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.extract.bluesky import ExtractorBluesky
from src.extract.telegram import ExtractorTelegram
from src.extract.youtube import ExtractorYouTube
from src.models import Plataforma
from src.storage import guardar_extraccion

_console = Console()


@click.command()
@click.option(
    "--plataforma",
    type=click.Choice([p.value for p in Plataforma if p != Plataforma.OTRA]),
    required=True,
    help="Plataforma desde la que extraer.",
)
@click.option("--termino", type=str, default=None, help="Termino de busqueda (Bluesky).")
@click.option("--canal", type=str, default=None, help="Canal de Telegram (@username).")
@click.option("--video-id", type=str, default=None, help="ID o URL de video de YouTube.")
@click.option("--limite", type=int, default=100, show_default=True, help="Maximo de posts a capturar.")
@click.option("--no-guardar", is_flag=True, default=False, help="No guardar en Parquet.")
def main(plataforma: str, termino: str | None, canal: str | None, video_id: str | None, limite: int, no_guardar: bool) -> None:
    if plataforma == Plataforma.BLUESKY.value and not termino:
        _console.print("[red]✗[/red] Bluesky requiere --termino.")
        sys.exit(1)
    if plataforma == Plataforma.TELEGRAM.value and not canal:
        _console.print("[red]✗[/red] Telegram requiere --canal.")
        sys.exit(1)
    if plataforma == Plataforma.YOUTUBE.value and not video_id:
        _console.print("[red]✗[/red] YouTube requiere --video-id.")
        sys.exit(1)

    if termino:
        desc = f"Termino: '[cyan]{termino}[/cyan]'"
    elif canal:
        desc = f"Canal: [cyan]{canal}[/cyan]"
    else:
        desc = f"Video: [cyan]{video_id}[/cyan]"

    _console.print(
        Panel.fit(
            f"[bold]Operacion Botin[/bold] — Pipeline de extraccion\n"
            f"Plataforma: [cyan]{plataforma}[/cyan] · {desc} · Limite: {limite}",
            border_style="red",
        )
    )

    if plataforma == Plataforma.BLUESKY.value:
        extractor = ExtractorBluesky()
        resultado = extractor.buscar_posts(termino=termino or "", limite=limite)
    elif plataforma == Plataforma.TELEGRAM.value:
        extractor = ExtractorTelegram()
        resultado = extractor.capturar_mensajes(canal=canal or "", limite=limite)
    elif plataforma == Plataforma.YOUTUBE.value:
        extractor = ExtractorYouTube()
        resultado = extractor.capturar_comentarios(video_id=video_id or "", limite=limite)
    else:
        _console.print(f"[red]✗[/red] Extractor para '{plataforma}' aun no implementado.")
        sys.exit(1)

    _mostrar_resumen(resultado)

    if not no_guardar and resultado.posts:
        guardar_extraccion(resultado)
    elif not resultado.posts:
        _console.print("[yellow]⚠[/yellow] No se capturaron posts. Nada que guardar.")

    _console.print("\n[bold green]✓ Extraccion completa.[/bold green]")


def _mostrar_resumen(resultado: Any) -> None:
    table = Table(title=f"Resumen — {resultado.plataforma.value}", show_header=True)
    table.add_column("Metrica", style="cyan", no_wrap=True)
    table.add_column("Valor", style="white")
    table.add_row("Plataforma", resultado.plataforma.value)
    table.add_row("Termino/Canal/Video", resultado.termino_busqueda or "—")
    table.add_row("Posts capturados", str(resultado.total_capturados))
    table.add_row("Errores", str(len(resultado.errores)))
    table.add_row("Duracion", f"{resultado.duracion_segundos:.2f}s")
    _console.print(table)

    if resultado.errores:
        _console.print("\n[yellow]Errores:[/yellow]")
        for err in resultado.errores[:5]:
            _console.print(f"  • {err}")

    if resultado.posts:
        _console.print("\n[cyan]Primeros posts capturados:[/cyan]")
        posts_table = Table(show_header=True, header_style="bold magenta")
        posts_table.add_column("Autor", style="cyan", no_wrap=True)
        posts_table.add_column("Fecha", style="dim")
        posts_table.add_column("Texto (primeros 80 chars)", overflow="fold")
        for post in resultado.posts[:5]:
            texto_corto = post.texto[:80] + ("..." if len(post.texto) > 80 else "")
            texto_corto = texto_corto.replace("\n", " ")
            posts_table.add_row(
                post.autor_handle,
                post.fecha_publicacion.strftime("%Y-%m-%d %H:%M"),
                texto_corto,
            )
        _console.print(posts_table)


if __name__ == "__main__":
    main()
