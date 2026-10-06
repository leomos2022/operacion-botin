# TASKS.md — Checklist de fases

> Marca cada tarea como `EN CURSO`, `HECHA` o `PENDIENTE`.
> Una tarea solo se marca `HECHA` después de commit + verificación.

---

## FASE 0 — Cimientos

- [HECHA] **0.1 — Scaffolding monorepo**: estructura de carpetas, git, apps/web base, apps/api base, pipeline base, packages/shared, CI, docs raíz.
- [HECHA] **0.2 — Sistema de diseño**: tailwind config completo, componentes base (Botón, Tarjeta, Badge, Stat, Tabla), tokens de tipografía y espaciado, storybook o página de muestra.
- [HECHA] **0.3 — Layout y navegación**: header responsive con menú móvil, footer con licencias, layout base reutilizable, rutas (índice, casos, industria, metodología, verifica).
- [HECHA] **0.4 — Home scrollytelling**: hero con headline, secciones narrativas con scroll, visualizaciones placeholder, CTA a metodología.
- [HECHA] **0.5 — Página de Metodología**: definiciones (bot, troll, cuenta falsa, operador coordinado), flujo de recolección, criterios de etiquetado, limitaciones.
- [HECHA] **0.6 — Páginas de contenido inicial**: índice de casos (vacío con estructura), La Industria (placeholder), Verifica (placeholder con formulario de reporte).
- [HECHA] **0.7 — SEO y ADRs**: meta tags OG/Twitter, sitemap, robots.txt, primer ADR (selección de stack), primer ADR (categorización de bots).
- [HECHA] **0.8 — Auditoría de fuentes y deploy**: revisión de datos placeholder, deploy web a Cloudflare Pages, deploy API a Workers, smoke test post-deploy.

---

## FASE 1 — Pipeline de extracción

- [HECHA] **1.1 — Configuración de credenciales**: definir qué APIs tenemos acceso, configurar `.env`, validar acceso.
- [HECHA] **1.2 — Extractor Bluesky** (API abierta, sin costo): captura de posts públicos por término, DID de cuentas, hilos.
- [PENDIENTE] **1.3 — Extractor Telegram** (bot observador en canales públicos): captura de mensajes por canal.
- [PENDIENTE] **1.4 — Extractor Twitter/X** (API v2 tier gratuito, limitado): captura de timelines y mentions de cuentas de interés.
- [HECHA] **1.5 — Esquema común de registros**: modelo Pydantic para `PostCapturado` con marca de tiempo, plataforma, fuente, hash.
- [HECHA] **1.6 — Almacenamiento local**: guardado en Parquet particionado por fecha + JSON de validación.
- [HECHA] **1.7 — CLI de extracción**: comando `uv run python -m src.extract --plataforma bluesky --termino "elecciones 2026"`.
- [HECHA] **1.8 — Documentación del pipeline**: README de `pipeline/` con comandos y troubleshooting.

---

## FASES POSTERIORES (borrador — se detallan al cerrar Fase 1)

- **FASE 2** — Modelo de features y etiquetado
- **FASE 3** — RAG y buscador semántico
- **FASE 4** — Casos documentados (contenido editorial)
- **FASE 5** — Visualizaciones interactivas
- **FASE 6** — Lanzamiento y difusión
