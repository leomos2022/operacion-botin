"""Modelos de datos compartidos por los módulos del pipeline.

Todos los extractores (Bluesky, Telegram, Twitter) producen registros
que se ajustan a `PostCapturado`. Esto garantiza que el resto del
pipeline (features, almacenamiento, RAG) pueda consumir datos de
cualquier plataforma de forma uniforme.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Plataforma(StrEnum):
    """Plataformas soportadas por el pipeline."""

    BLUESKY = "bluesky"
    TELEGRAM = "telegram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    OTRA = "otra"


class MetodoCaptura(StrEnum):
    """Cómo se obtuvo el registro. Importante para auditoría."""

    API_OFICIAL = "api_oficial"
    SCRAPING_PUBLICO = "scraping_publico"
    REPORTE_CIUDADANO = "reporte_ciudadano"
    FIREHOSE = "firehose"


class PostCapturado(BaseModel):
    """Registro único de un post/captura pública.

    Reglas editoriales (AGENT_RULES.md §4):
    - Solo contenido público. Nunca mensajes privados.
    - El `id_plataforma` se conserva tal cual (se seudonimiza después,
      en la fase de features, al etiquetar).
    - `url` debe ser accesible públicamente.
    - `hash_contenido` permite detectar ediciones posteriores.
    """

    # Identificación
    id_plataforma: str = Field(
        ...,
        description="ID del post en la plataforma (ej. AT URI en Bluesky, message_id en Telegram)",
    )
    plataforma: Plataforma
    metodo_captura: MetodoCaptura

    # Autor (se conservará hasta la fase de seudonimización)
    autor_handle: str = Field(
        ...,
        description="Handle público del autor (ej. @usuario.bsky.social, @usuario en Telegram)",
    )
    autor_id_plataforma: str = Field(
        ...,
        description="ID interno del autor en la plataforma (DID en Bluesky, user_id en Telegram)",
    )

    # Contenido
    texto: str = Field(..., description="Texto del post, sin recortes")
    url: str = Field(..., description="URL pública del post")
    fecha_publicacion: datetime = Field(
        ...,
        description="Fecha de publicación del post en UTC",
    )

    # Metadatos de captura
    fecha_captura: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Momento en que capturamos el post (UTC)",
    )
    termino_busqueda: str | None = Field(
        default=None,
        description="Término que disparó la captura (si aplica)",
    )

    # Hash para detectar ediciones
    hash_contenido: str = Field(
        ...,
        description="SHA-256 del texto + url, para detectar ediciones posteriores",
    )

    # Metadatos opcionales específicos de plataforma
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Campos extra específicos de la plataforma (likes, reposts, etc.)",
    )

    @field_validator("fecha_publicacion", "fecha_captura")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        """Garantiza que todas las fechas llevan tz info UTC."""
        if v.tzinfo is None:
            raise ValueError("La fecha debe tener tz info (UTC)")
        return v.astimezone(UTC)

    @staticmethod
    def calcular_hash(texto: str, url: str) -> str:
        """Calcula SHA-256 del contenido para detectar ediciones."""
        h = hashlib.sha256()
        h.update(texto.encode("utf-8"))
        h.update(b"|")
        h.update(url.encode("utf-8"))
        return h.hexdigest()


class ResultadoExtraccion(BaseModel):
    """Resultado de una corrida del extractor.

    Facilita logging, métricas y debugging.
    """

    plataforma: Plataforma
    termino_busqueda: str | None = None
    total_capturados: int
    posts: list[PostCapturado] = Field(default_factory=list)
    errores: list[str] = Field(default_factory=list)
    fecha_inicio: datetime
    fecha_fin: datetime

    @property
    def duracion_segundos(self) -> float:
        return (self.fecha_fin - self.fecha_inicio).total_seconds()
