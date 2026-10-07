"""Extractor de YouTube (Data API v3).

Captura comentarios de videos publicos. La API v3 permite:
- Buscar videos por termino
- Listar comentarios de un video (commentThreads.list)
- Obtener info del video (videos.list)

Reglas editoriales (AGENT_RULES.md §4):
- Solo videos y comentarios publicos.
- Cada comentario capturado lleva marca de tiempo UTC, URL publica y hash.
- Respeta cuota diaria de la API (10.000 unidades/dia por defecto).
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress

from src.models import MetodoCaptura, Plataforma, PostCapturado, ResultadoExtraccion

_console = Console()

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


class ExtractorYouTube:
    """Cliente YouTube Data API v3 para captura de comentarios publicos."""

    def __init__(self) -> None:
        load_dotenv()
        self.api_key: str | None = os.getenv("YOUTUBE_API_KEY")

    @property
    def auth_params(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError(
                "Falta YOUTUBE_API_KEY en .env. "
                "Consiguela en Google Cloud Console -> APIs & Services -> Credentials."
            )
        return {"key": self.api_key}

    def verificar_acceso(self) -> dict[str, Any]:
        """Verifica que la API key funciona con una llamada simple."""
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                f"{YOUTUBE_API_BASE}/videos",
                params={**self.auth_params, "part": "snippet", "id": "jNQXAC9IVRw"},
            )
            resp.raise_for_status()
            data = resp.json()
        if "error" in data:
            raise RuntimeError(f"YouTube API error: {data['error']['message']}")
        _console.print("[green]✓[/green] YouTube Data API v3 responde correctamente")
        return data

    def obtener_info_video(self, video_id: str) -> dict[str, Any] | None:
        """Obtiene info del video (titulo, canal, fecha)."""
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                f"{YOUTUBE_API_BASE}/videos",
                params={**self.auth_params, "part": "snippet,statistics", "id": video_id},
            )
            resp.raise_for_status()
            data = resp.json()
        items = data.get("items", [])
        if not items:
            return None
        return items[0]

    def capturar_comentarios(
        self,
        video_id: str,
        limite: int = 100,
    ) -> ResultadoExtraccion:
        """Captura comentarios de un video publico."""
        inicio = datetime.now(UTC)

        # Extraer video_id si viene como URL
        if "watch?v=" in video_id:
            video_id = video_id.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in video_id:
            video_id = video_id.split("youtu.be/")[1].split("?")[0]

        _console.print(
            f"[cyan]→[/cyan] Capturando comentarios de video [bold]{video_id}[/bold] (limite: {limite})"
        )

        self.verificar_acceso()

        info_video = self.obtener_info_video(video_id)
        if not info_video:
            error_msg = f"Video {video_id} no encontrado o no es publico"
            _console.print(f"[red]✗[/red] {error_msg}")
            return ResultadoExtraccion(
                plataforma=Plataforma.YOUTUBE,
                termino_busqueda=video_id,
                total_capturados=0,
                posts=[],
                errores=[error_msg],
                fecha_inicio=inicio,
                fecha_fin=datetime.now(UTC),
            )

        titulo_video = info_video["snippet"]["title"]
        canal_video = info_video["snippet"]["channelTitle"]
        _console.print(
            f"[green]✓[/green] Video: [bold]{titulo_video}[/bold] · Canal: {canal_video}"
        )

        comentarios_capturados: list[PostCapturado] = []
        errores: list[str] = []
        next_page_token: str | None = None
        total_api_calls = 0

        try:
            with Progress() as progress:
                tarea = progress.add_task("[cyan]Capturando comentarios...", total=limite)

                with httpx.Client(timeout=60) as client:
                    while len(comentarios_capturados) < limite:
                        params: dict[str, Any] = {
                            **self.auth_params,
                            "part": "snippet",
                            "videoId": video_id,
                            "maxResults": min(100, limite - len(comentarios_capturados)),
                            "order": "time",
                            "textFormat": "plainText",
                        }
                        if next_page_token:
                            params["pageToken"] = next_page_token

                        resp = client.get(
                            f"{YOUTUBE_API_BASE}/commentThreads",
                            params=params,
                        )
                        total_api_calls += 1
                        data = resp.json()

                        if "error" in data:
                            error_msg = data["error"]["message"]
                            errores.append(f"YouTube API: {error_msg}")
                            _console.print(
                                f"[yellow]⚠[/yellow] API devolvio error: {error_msg}"
                            )
                            break

                        items = data.get("items", [])
                        if not items:
                            break

                        for item in items:
                            try:
                                post = self._convertir_comentario(
                                    item, video_id, titulo_video, canal_video
                                )
                                if post is not None:
                                    comentarios_capturados.append(post)
                                    progress.advance(tarea)
                                    if len(comentarios_capturados) >= limite:
                                        break
                            except Exception as exc:
                                errores.append(f"Error procesando comentario: {exc}")

                        next_page_token = data.get("nextPageToken")
                        if not next_page_token:
                            break

            _console.print(
                f"[green]✓[/green] {len(comentarios_capturados)} comentarios capturados "
                f"({total_api_calls} llamadas API)"
            )

        except Exception as exc:
            errores.append(f"Error en captura: {exc}")

        fin = datetime.now(UTC)

        return ResultadoExtraccion(
            plataforma=Plataforma.YOUTUBE,
            termino_busqueda=video_id,
            total_capturados=len(comentarios_capturados),
            posts=comentarios_capturados,
            errores=errores,
            fecha_inicio=inicio,
            fecha_fin=fin,
        )

    def _convertir_comentario(
        self,
        item: dict[str, Any],
        video_id: str,
        titulo_video: str,
        canal_video: str,
    ) -> PostCapturado | None:
        """Convierte un commentThread item a nuestro modelo PostCapturado."""
        top_comment = item.get("snippet", {}).get("topLevelComment", {})
        snippet = top_comment.get("snippet", {})

        texto = snippet.get("textDisplay") or snippet.get("textOriginal") or ""
        if not texto.strip():
            return None

        fecha_pub_str = snippet.get("publishedAt", "")
        fecha_pub = datetime.fromisoformat(fecha_pub_str.replace("Z", "+00:00"))

        autor_handle = snippet.get("authorDisplayName", "anonimo")
        autor_id = snippet.get("authorChannelId", {}).get("value", "unknown")

        comment_id = top_comment.get("id", "")
        url = f"https://www.youtube.com/watch?v={video_id}&lc={comment_id}"

        metadata: dict[str, Any] = {
            "video_id": video_id,
            "video_title": titulo_video,
            "video_channel": canal_video,
            "comment_id": comment_id,
            "like_count": snippet.get("likeCount", 0),
            "reply_count": item.get("snippet", {}).get("totalReplyCount", 0),
            "is_reply": False,
            "author_profile_image": snippet.get("authorProfileImageUrl"),
            "parent_comment_id": None,
        }

        return PostCapturado(
            id_plataforma=f"youtube_{comment_id}",
            plataforma=Plataforma.YOUTUBE,
            metodo_captura=MetodoCaptura.API_OFICIAL,
            autor_handle=autor_handle,
            autor_id_plataforma=str(autor_id),
            texto=texto,
            url=url,
            fecha_publicacion=fecha_pub,
            termino_busqueda=video_id,
            hash_contenido=PostCapturado.calcular_hash(texto, url),
            metadata=metadata,
        )
