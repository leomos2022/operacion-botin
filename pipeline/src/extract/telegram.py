"""Extractor de Telegram (MTProto API via telethon).

Captura mensajes de cualquier canal público de Telegram sin necesidad
de ser miembro. Esto es lo que diferencia MTProto de la Bot API:
acceso completo a contenido público.

Reglas editoriales (AGENT_RULES.md §4):
- Solo canales públicos. No grupos privados ni DMs.
- Cada mensaje capturado lleva marca de tiempo UTC, URL pública y hash.
- Respeta rate-limits de Telegram (FloodWait).

Requisitos:
- TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE en .env
- La primera vez que se ejecuta, telethon pide un código de login
  enviado al Telegram del usuario. Se crea un archivo de sesión
  (.session) que persiste para usos futuros.
"""

from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from telethon import TelegramClient
from telethon.tl.types import Message

from src.models import MetodoCaptura, Plataforma, PostCapturado, ResultadoExtraccion

_console = Console()


class ExtractorTelegram:
    """Extractor MTProto de Telegram para canales públicos."""

    def __init__(self) -> None:
        load_dotenv()
        self.api_id: str | None = os.getenv("TELEGRAM_API_ID")
        self.api_hash: str | None = os.getenv("TELEGRAM_API_HASH")
        self.phone: str | None = os.getenv("TELEGRAM_PHONE")
        self._client: TelegramClient | None = None
        # Archivo de sesión: persiste el login para no pedir código cada vez
        self.session_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            ".session",
            "operacion_botin_telegram",
        )

    @property
    def client(self) -> TelegramClient:
        """Cliente telethon perezoso: crea sesión si no existe."""
        if self._client is None:
            if not self.api_id or not self.api_hash or not self.phone:
                raise RuntimeError(
                    "Faltan credenciales MTProto en .env. "
                    "Configura TELEGRAM_API_ID, TELEGRAM_API_HASH y TELEGRAM_PHONE. "
                    "Consígelas en https://my.telegram.org -> API development tools."
                )
            # Crear directorio de sesión si no existe
            os.makedirs(os.path.dirname(self.session_path), exist_ok=True)
            self._client = TelegramClient(
                self.session_path,
                int(self.api_id),
                self.api_hash,
            )
        return self._client

    async def _iniciar_sesion(self) -> None:
        """Inicia sesión. La primera vez pide código por Telegram."""
        if not self.client.is_connected():
            await self.client.connect()
            if not await self.client.is_user_authorized():
                _console.print(
                    "[cyan]→[/cyan] Iniciando sesión en Telegram por primera vez..."
                )
                await self.client.send_code_request(self.phone)
                codigo = input(
                    "  Introduce el código recibido en tu Telegram: "
                ).strip()
                await self.client.sign_in(self.phone, codigo)
            _console.print("[green]✓[/green] Sesión Telegram activa")

    async def _capturar_async(
        self,
        canal: str,
        limite: int,
    ) -> ResultadoExtraccion:
        """Método asíncrono que hace el trabajo real."""
        inicio = datetime.now(UTC)
        _console.print(
            f"[cyan]→[/cyan] Capturando mensajes de [bold]{canal}[/bold] (límite: {limite})"
        )

        await self._iniciar_sesion()

        mensajes_capturados: list[PostCapturado] = []
        errores: list[str] = []

        try:
            # Resolver el canal (acepta @username, t.me/joinchat/, o ID)
            entidad = await self.client.get_entity(canal)

            # Info del canal
            canal_username = getattr(entidad, "username", None)
            canal_title = getattr(entidad, "title", canal)
            canal_id = getattr(entidad, "id", 0)

            _console.print(
                f"[green]✓[/green] Canal: [bold]{canal_title}[/bold]"
                + (f" (@{canal_username})" if canal_username else "")
                + f" (id: {canal_id})"
            )

            # Iterar mensajes del historial (más recientes primero)
            count = 0
            async for message in self.client.iter_messages(entidad, limit=limite):
                try:
                    post = self._convertir_mensaje(
                        message, entidad, canal_username, canal_title, canal_id
                    )
                    if post is not None:
                        mensajes_capturados.append(post)
                        count += 1
                except Exception as exc:
                    errores.append(f"Error procesando mensaje {message.id}: {exc}")

            _console.print(f"[green]✓[/green] {count} mensajes capturados")

        except Exception as exc:
            errores.append(f"Error en captura: {exc}")

        fin = datetime.now(UTC)

        return ResultadoExtraccion(
            plataforma=Plataforma.TELEGRAM,
            termino_busqueda=canal,
            total_capturados=len(mensajes_capturados),
            posts=mensajes_capturados,
            errores=errores,
            fecha_inicio=inicio,
            fecha_fin=fin,
        )

    def capturar_mensajes(
        self,
        canal: str,
        limite: int = 50,
    ) -> ResultadoExtraccion:
        """Captura los últimos mensajes de un canal público."""
        return asyncio.run(self._capturar_async(canal, limite))

    def _convertir_mensaje(
        self,
        message: Message,
        entidad: Any,
        canal_username: str | None,
        canal_title: str,
        canal_id: int,
    ) -> PostCapturado | None:
        """Convierte un mensaje de telethon a nuestro modelo PostCapturado."""
        texto = message.text or message.message or ""
        if not texto.strip():
            return None

        fecha_pub = message.date
        if fecha_pub.tzinfo is None:
            fecha_pub = fecha_pub.replace(tzinfo=UTC)
        else:
            fecha_pub = fecha_pub.astimezone(UTC)

        sender = getattr(message, "sender", None)
        if sender and not isinstance(entidad, type(sender)):
            autor_handle = getattr(sender, "username", None) or str(getattr(sender, "id", canal_id))
            autor_id = str(getattr(sender, "id", canal_id))
        else:
            autor_handle = canal_username or canal_title
            autor_id = str(canal_id)

        msg_id = message.id
        if canal_username:
            url = f"https://t.me/{canal_username}/{msg_id}"
        else:
            url = f"https://t.me/c/{str(canal_id)[4:]}/{msg_id}" if str(canal_id).startswith("-100") else f"telegram://channel/{canal_id}/{msg_id}"

        metadata: dict[str, Any] = {
            "canal_id": canal_id,
            "canal_title": canal_title,
            "canal_username": canal_username,
            "message_id": msg_id,
            "edit_date": message.edit_date.isoformat() if message.edit_date else None,
            "is_forward": message.forward is not None,
            "views": getattr(message, "views", None),
            "forwards": getattr(message, "forwards", None),
            "replies": getattr(message.replies, "replies", None) if message.replies else None,
            "media": bool(message.media),
        }

        return PostCapturado(
            id_plataforma=f"{canal_id}_{msg_id}",
            plataforma=Plataforma.TELEGRAM,
            metodo_captura=MetodoCaptura.API_OFICIAL,
            autor_handle=autor_handle,
            autor_id_plataforma=autor_id,
            texto=texto,
            url=url,
            fecha_publicacion=fecha_pub,
            termino_busqueda=canal_username or str(canal_id),
            hash_contenido=PostCapturado.calcular_hash(texto, url),
            metadata=metadata,
        )
