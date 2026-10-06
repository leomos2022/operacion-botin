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
- [PENDIENTE] **0.6 — Páginas de contenido inicial**: índice de casos (vacío con estructura), La Industria (placeholder), Verifica (placeholder con formulario de reporte).
- [PENDIENTE] **0.7 — SEO y ADRs**: meta tags OG/Twitter, sitemap, robots.txt, primer ADR (selección de stack), primer ADR (categorización de bots).
- [PENDIENTE] **0.8 — Auditoría de fuentes y deploy**: revisión de datos placeholder, deploy web a Cloudflare Pages, deploy API a Workers, smoke test post-deploy.

---

## FASES POSTERIORES (borrador — se detallan al cerrar Fase 0)

- **FASE 1** — Pipeline de extracción (Twitter/Telegram/Bluesky)
- **FASE 2** — Modelo de features y etiquetado
- **FASE 3** — RAG y buscador semántico
- **FASE 4** — Casos documentados (contenido editorial)
- **FASE 5** — Visualizaciones interactivas
- **FASE 6** — Lanzamiento ydifusión
