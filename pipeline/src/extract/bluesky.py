"""Extractor de Bluesky (AT Protocol).

Captura posts públicos por término de búsqueda. Usa el SDK oficial
`atproto` que se comunica con la API pública de bsky.social.

Reglas editoriales (AGENT_RULES.md §4):
- Solo posts públicos (no DMs ni contenido privado).
- Respeta rate-limit del SDK.
- Cada post capturado lleva marca de tiempo UTC, URL pública y hash
  de contenido para detectar ediciones posteriores.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from atproto import Client
from atproto_client.models.app.bsky.feed.search_posts import Params as SearchPostsParams
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress

from src.models import MetodoCaptura, Plataforma, PostCapturado, ResultadoExtraccion

_console = Console()


class ExtractorBluesky:
    """Cliente wrapper sobre atproto.Client para búsquedas públicas."""

    def __init__(self) -> None:
        load_dotenv()  # carga .env desde la raíz del monorepo
        self.handle: str | None = os.getenv("BLUESKY_HANDLE")
        self.password: str | None = os.getenv("BLUESKY_APP_PASSWORD")
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        """Client perezoso: solo se autentica cuando se usa por primera vez."""
        if self._client is None:
            if not self.handle or not self.password:
                raise RuntimeError(
                    "Faltan credenciales de Bluesky en .env. "
                    "Configura BLUESKY_HANDLE y BLUESKY_APP_PASSWORD."
                )
            self._client = Client()
            self._client.login(self.handle, self.password)
            _console.print(
                f"[green]✓[/green] Sesión iniciada en Bluesky como [bold]{self.handle}[/bold]"
            )
        return self._client

    def buscar_posts(
        self,
        termino: str,
        limite: int = 100,
    ) -> ResultadoExtraccion:
        """Busca posts públicos que contengan el término.

        Args:
            termino: texto a buscar (p. ej. "elecciones Colombia").
            limite: máximo de posts a capturar (default 100, max 100 por
                limitación de la API).

        Returns:
            ResultadoExtraccion con los posts capturados y errores si los hubo.
        """
        inicio = datetime.now(UTC)
        _console.print(
            f"[cyan]→[/cyan] Buscando en Bluesky: '[bold]{termino}[/bold]' "
            f"(límite: {limite})"
        )

        posts_capturados: list[PostCapturado] = []
        errores: list[str] = []

        try:
            params = SearchPostsParams(
                q=termino,
                limit=limite,
            )
            response = self.client.app.bsky.feed.search_posts(params=params)

            posts_encontrados = response.posts
            _console.print(
                f"[green]✓[/green] {len(posts_encontrados)} posts recibidos de la API"
            )

            with Progress() as progress:
                tarea = progress.add_task(
                    "[cyan]Procesando posts...", total=len(posts_encontrados)
                )

                for post_view in posts_encontrados:
                    try:
                        post = self._convertir_post(post_view, termino)
                        if post is not None:
                            posts_capturados.append(post)
                    except Exception as exc:
                        errores.append(
                            f"Error procesando post {getattr(post_view, 'uri', '?')}: {exc}"
                        )
                    progress.advance(tarea)

        except Exception as exc:
            errores.append(f"Error en búsqueda: {exc}")

        fin = datetime.now(UTC)

        return ResultadoExtraccion(
            plataforma=Plataforma.BLUESKY,
            termino_busqueda=termino,
            total_capturados=len(posts_capturados),
            posts=posts_capturados,
            errores=errores,
            fecha_inicio=inicio,
            fecha_fin=fin,
        )

    def _convertir_post(
        self,
        post_view: Any,
        termino: str,
    ) -> PostCapturado | None:
        """Convierte un PostView de atproto a nuestro modelo PostCapturado."""
        texto = ""
        if hasattr(post_view, "record") and hasattr(post_view.record, "text"):
            texto = post_view.record.text or ""

        if not texto.strip():
            return None

        author_handle = post_view.author.handle
        uri = post_view.uri
        rkey = uri.split("/")[-1] if uri else ""
        url = f"https://bsky.app/profile/{author_handle}/post/{rkey}"

        fecha_pub_str = ""
        if hasattr(post_view, "record") and hasattr(post_view.record, "created_at"):
            fecha_pub_str = post_view.record.created_at
        fecha_pub = datetime.fromisoformat(fecha_pub_str.replace("Z", "+00:00"))

        metadata: dict[str, Any] = {}
        if hasattr(post_view, "like_count"):
            metadata["like_count"] = post_view.like_count
        if hasattr(post_view, "repost_count"):
            metadata["repost_count"] = post_view.repost_count
        if hasattr(post_view, "reply_count"):
            metadata["reply_count"] = post_view.reply_count
        if hasattr(post_view, "indexed_at"):
            metadata["indexed_at"] = post_view.indexed_at

        return PostCapturado(
            id_plataforma=post_view.uri,
            plataforma=Plataforma.BLUESKY,
            metodo_captura=MetodoCaptura.API_OFICIAL,
            autor_handle=author_handle,
            autor_id_plataforma=post_view.author.did,
            texto=texto,
            url=url,
            fecha_publicacion=fecha_pub,
            termino_busqueda=termino,
            hash_contenido=PostCapturado.calcular_hash(texto, url),
            metadata=metadata,
        )
