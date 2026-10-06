"""Análisis de features para detección de patrones.

Tres familias de análisis (ver ADR-0002 y metodología §03):
- Señales temporales: ¿hay publicación no humana?
- Señales de contenido: ¿hay repetición o plantillas?
- Señales de grafo: ¿hay coordinación entre cuentas?

Cada análisis produce métricas y etiquetas candidatas con confianza.
Ninguna etiqueta se publica sin revisión humana (metodología §03).
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from rich.console import Console
from rich.table import Table

from src.features.seudonimizacion import es_publico_permitido, seudonimizar
from src.models import Plataforma

_console = Console()

_REPO_ROOT = Path(__file__).resolve().parents[3]
_RAW_DIR = _REPO_ROOT / "packages" / "shared" / "data" / "raw"
_HALLAZGOS_DIR = _REPO_ROOT / "packages" / "shared" / "data" / "hallazgos"


def cargar_posts_bluesky() -> pd.DataFrame:
    """Carga todos los Parquet de Bluesky disponibles."""
    archivos = list(_RAW_DIR.glob("bluesky/**/*.parquet"))
    if not archivos:
        raise RuntimeError(
            f"No se encontraron Parquet en {_RAW_DIR / "bluesky"}. "
            "Ejecuta primero el extractor."
        )
    dfs = [pd.read_parquet(a) for a in archivos]
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset=["id_plataforma"]).reset_index(drop=True)
    return df


def analizar_temporal(df: pd.DataFrame) -> dict[str, Any]:
    """Análisis de señales temporales por autor."""
    _console.print("[cyan]→[/cyan] Análisis temporal...")

    df["fecha_pub_dt"] = pd.to_datetime(df["fecha_publicacion"], format="ISO8601", utc=True)
    df["hora"] = df["fecha_pub_dt"].dt.hour

    por_autor: dict[str, Any] = {}

    for handle, grupo in df.groupby("autor_handle"):
        if len(grupo) < 3:
            continue

        horas = grupo["hora"].tolist()
        horas_unicas = sorted(set(horas))
        cobertura = len(horas_unicas) / 24.0

        posts_madrugada = sum(1 for h in horas if 2 <= h < 5)
        ratio_madrugada = posts_madrugada / len(grupo)

        fechas_ordenadas = grupo["fecha_pub_dt"].sort_values()
        intervalos = fechas_ordenadas.diff().dropna().dt.total_seconds()
        intervalo_medio = float(intervalos.mean()) if len(intervalos) > 0 else 0
        intervalo_std = float(intervalos.std()) if len(intervalos) > 1 else 0
        cv = intervalo_std / intervalo_medio if intervalo_medio > 0 else 0

        senal_cobertura = cobertura > 0.5 and ratio_madrugada > 0.2
        senal_regularidad = cv < 0.2 and len(grupo) >= 10
        confianza = 0.0
        if senal_cobertura and senal_regularidad:
            confianza = 0.85
        elif senal_cobertura or senal_regularidad:
            confianza = 0.65

        por_autor[handle] = {
            "total_posts": len(grupo),
            "horas_unicas": len(horas_unicas),
            "cobertura_horaria_pct": round(cobertura * 100, 1),
            "ratio_madrugada_pct": round(ratio_madrugada * 100, 1),
            "intervalo_medio_seg": round(intervalo_medio, 1),
            "cv_intervalos": round(cv, 3),
            "senal_cobertura": senal_cobertura,
            "senal_regularidad": senal_regularidad,
            "confianza_bot_candidato": round(confianza, 2),
        }

    return {"por_autor": por_autor}


def analizar_contenido(df: pd.DataFrame) -> dict[str, Any]:
    """Análisis de señales de contenido: textos repetidos, hashtags."""
    _console.print("[cyan]→[/cyan] Análisis de contenido...")

    df["texto_normalizado"] = df["texto"].str.lower().str.strip()
    duplicados = df[df.duplicated(subset=["texto_normalizado"], keep=False)]
    textos_repetidos: list[dict[str, Any]] = []
    for texto, grupo in duplicados.groupby("texto_normalizado"):
        if len(grupo) < 2:
            continue
        autores = grupo["autor_handle"].unique().tolist()
        if len(autores) > 1:
            textos_repetidos.append({
                "texto_preview": texto[:120],
                "autores": [seudonimizar(a).seudonimo for a in autores],
                "total_repeticiones": len(grupo),
            })

    todos_textos = " ".join(df["texto"].tolist())
    hashtags = re.findall(r"#\w+", todos_textos)
    hashtags_counter = Counter(hashtags)
    top_hashtags = hashtags_counter.most_common(15)

    return {
        "textos_repetidos_entre_cuentas": textos_repetidos,
        "total_textos_repetidos": len(textos_repetidos),
        "top_hashtags": top_hashtags,
    }


def analizar_grafo(df: pd.DataFrame) -> dict[str, Any]:
    """Análisis de señales de grafo: sincronías temporales."""
    _console.print("[cyan]→[/cyan] Análisis de grafo...")

    df["fecha_pub_dt"] = pd.to_datetime(df["fecha_publicacion"], format="ISO8601", utc=True)
    df = df.sort_values("fecha_pub_dt").reset_index(drop=True)

    sincronias: list[dict[str, Any]] = []
    ventana_segundos = 60

    for i, row_i in df.iterrows():
        for j in range(i + 1, len(df)):
            row_j = df.iloc[j]
            delta = abs((row_j["fecha_pub_dt"] - row_i["fecha_pub_dt"]).total_seconds())
            if delta > ventana_segundos:
                break
            if row_i["autor_handle"] != row_j["autor_handle"]:
                palabras_i = set(row_i["texto"].lower().split())
                palabras_j = set(row_j["texto"].lower().split())
                if not palabras_i or not palabras_j:
                    continue
                jaccard = len(palabras_i & palabras_j) / len(palabras_i | palabras_j)
                if jaccard > 0.3:
                    sincronias.append({
                        "autor_1": seudonimizar(row_i["autor_handle"]).seudonimo,
                        "autor_2": seudonimizar(row_j["autor_handle"]).seudonimo,
                        "delta_segundos": round(delta, 1),
                        "similitud_texto": round(jaccard, 2),
                        "timestamp": row_i["fecha_pub_dt"].isoformat(),
                    })

    return {
        "sincronias_detectadas": sincronias[:50],
        "total_sincronias": len(sincronias),
    }


def generar_hallazgos() -> dict[str, Any]:
    """Ejecuta los 3 análisis y produce un JSON consolidado de hallazgos."""
    _console.print("[bold]Cargando dataset Bluesky...[/bold]")
    df = cargar_posts_bluesky()
    _console.print(f"[green]✓[/green] {len(df)} posts únicos cargados")

    resumen = {
        "metadata": {
            "fecha_analisis": datetime.now().isoformat(),
            "plataforma": Plataforma.BLUESKY.value,
            "total_posts_unicos": len(df),
            "total_autores_unicos": df["autor_handle"].nunique(),
            "periodo_captura": {
                "inicio": df["fecha_publicacion"].min(),
                "fin": df["fecha_publicacion"].max(),
            },
            "terminos_busqueda": df["termino_busqueda"].unique().tolist(),
        },
        "top_autores_volumen": _top_autores_volumen(df),
        "analisis_temporal": analizar_temporal(df),
        "analisis_contenido": analizar_contenido(df),
        "analisis_grafo": analizar_grafo(df),
        "cuentas_con_senales": _cuentas_con_senales(df),
    }

    return resumen


def _top_autores_volumen(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Top 10 autores por volumen de posts, con seudónimo."""
    top = df["autor_handle"].value_counts().head(10)
    resultado = []
    for handle, count in top.items():
        sep = seudonimizar(handle)
        resultado.append({
            "seudonimo": sep.seudonimo,
            "handle_publico": handle if es_publico_permitido(handle) else None,
            "total_posts": int(count),
        })
    return resultado


def _cuentas_con_senales(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Cuentas que dispararon alguna señal de alerta en el análisis temporal."""
    temporal = analizar_temporal(df)
    cuentas_alerta = []
    for handle, metrics in temporal["por_autor"].items():
        if metrics["confianza_bot_candidato"] >= 0.65:
            sep = seudonimizar(handle)
            cuentas_alerta.append({
                "seudonimo": sep.seudonimo,
                "handle_publico": handle if es_publico_permitido(handle) else None,
                "confianza_bot_candidato": metrics["confianza_bot_candidato"],
                "total_posts": metrics["total_posts"],
                "razones": [
                    r for r, v in [
                        ("cobertura_horaria_amplia", metrics["senal_cobertura"]),
                        ("regularidad_mecanica_intervalos", metrics["senal_regularidad"]),
                    ] if v
                ],
            })
    cuentas_alerta.sort(key=lambda x: x["confianza_bot_candidato"], reverse=True)
    return cuentas_alerta


def guardar_hallazgos(hallazgos: dict[str, Any]) -> Path:
    """Guarda el JSON de hallazgos en packages/shared/data/hallazgos/."""
    _HALLAZGOS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _HALLAZGOS_DIR / f"hallazgos_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(hallazgos, f, ensure_ascii=False, indent=2, default=str)
    _console.print(f"[green]✓[/green] Hallazgos guardados en {path.relative_to(_REPO_ROOT)}")
    return path


def mostrar_resumen(hallazgos: dict[str, Any]) -> None:
    """Muestra tablas resumen en consola."""
    _console.print("\n[bold cyan]═══ RESUMEN DEL ANÁLISIS ═══[/bold cyan]")

    meta = hallazgos["metadata"]
    _console.print(f"\nTotal posts únicos: [bold]{meta["total_posts_unicos"]}[/bold]")
    _console.print(f"Autores únicos: [bold]{meta["total_autores_unicos"]}[/bold]")

    _console.print("\n[bold]Top 10 autores por volumen:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Seudónimo", style="cyan")
    table.add_column("Handle público", style="dim")
    table.add_column("Posts", justify="right")
    for a in hallazgos["top_autores_volumen"]:
        table.add_row(
            a["seudonimo"],
            a["handle_publico"] or "(seudonimizado)",
            str(a["total_posts"]),
        )
    _console.print(table)

    alertas = hallazgos["cuentas_con_senales"]
    if alertas:
        _console.print(f"\n[bold yellow]⚠ Cuentas con señales de alerta:[/bold yellow] ({len(alertas)})")
        alertas_table = Table(show_header=True, header_style="bold yellow")
        alertas_table.add_column("Seudónimo", style="yellow")
        alertas_table.add_column("Confianza", justify="right")
        alertas_table.add_column("Posts", justify="right")
        alertas_table.add_column("Razones")
        for a in alertas:
            alertas_table.add_row(
                a["seudonimo"],
                f"{a["confianza_bot_candidato"]:.2f}",
                str(a["total_posts"]),
                ", ".join(a["razones"]) or "—",
            )
        _console.print(alertas_table)
    else:
        _console.print("\n[green]✓ Ninguna cuenta disparó señales de alerta.[/green]")

    contenido = hallazgos["analisis_contenido"]
    _console.print("\n[bold]Análisis de contenido:[/bold]")
    _console.print(f"  Textos repetidos entre cuentas: {contenido["total_textos_repetidos"]}")
    if contenido["top_hashtags"]:
        _console.print("  Top hashtags:")
        for tag, count in contenido["top_hashtags"][:5]:
            _console.print(f"    {tag}: {count}")

    grafo = hallazgos["analisis_grafo"]
    _console.print("\n[bold]Análisis de grafo:[/bold]")
    _console.print(f"  Sincronías detectadas (ventana 60s): {grafo["total_sincronias"]}")
