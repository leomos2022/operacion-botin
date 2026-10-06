# ADR-0001: Selección de stack (Astro + Cloudflare + Python)

- **Estado**: Aceptado
- **Fecha**: 2026-10-05
- **Decisor**: equipo inicial Operación Botín

## Contexto

Operación Botín necesita una arquitectura que cumpla simultáneamente tres requisitos en tensión:

1. **Rendimiento y costo**: el sitio es estático en su mayoría (casos, metodología, industria). La audiencia es ciudadana, no interna; el tiempo de carga y el costo de hosting importan.
2. **Capacidad de cómputo asíncrono**: el pipeline de datos (extracción, features, RAG) es intensivo en CPU/red y se ejecuta periódicamente, no en línea con cada request.
3. **API ligera y observable**: el frontend necesita consumir datos etiquetados en runtime (búsqueda, listados filtrados), pero el volumen de tráfico esperado es bajo-moderado en Fase 0.

Además, el equipo es pequeño y valora:
- Bajo mantenimiento operativo (sin servidores que patchear)
- Banda ancha gratis / costo predecible
- Stack reproducible por terceros (la metodología es abierta; el código también debería poder auditarlo cualquiera)

## Decisión

Adoptamos el siguiente stack:

| Capa | Tecnología | Razón principal |
|------|------------|-----------------|
| Web (frontend) | **Astro 5** + Tailwind CSS 4 + React 19 (donde haga falta) | Astro genera HTML estático por defecto, lo que da rendimiento y SEO sin esfuerzo. React se usa solo para islas interactivas puntuales. |
| API | **Cloudflare Worker + Hono** | Workers ejecutan en edge, escalan a cero, cobran por request. Hono es minimalista y tipa bien con TS. Sin servidor que mantener. |
| Pipeline de datos | **Python 3.12 + uv** | Python es el estándar de facto para análisis de redes sociales y NLP. `uv` resuelve el infierno de dependencias más rápido que pip/poetry. |
| Compartido | **TypeScript types + JSON/Parquet** | Los tipos TS viven en `packages/shared` y los consumen `apps/web` y `apps/api`. Los datasets se publican como Parquet (compacto, tipado) o JSON (legible). |
| CI | **GitHub Actions** | Estándar, gratuito para OSS, integrado con el repositorio. |
| Deploy web | **Cloudflare Pages** | Integración nativa con Astro, dominio gratis, edge CDN. |
| Deploy API | **Cloudflare Workers** | Mismo motivo que API. |

## Consecuencias

**Positivas:**
- Costo de hosting cercano a cero en Fase 0 (Cloudflare free tier cubre el tráfico esperado).
- Deploy continuo sin infraestructura: push a `main` → Cloudflare despliega.
- TypeScript estricto en apps y shared → menos bugs en runtime.
- Python aislado en `pipeline/` → el equipo de datos puede iterar sin tocar el frontend.
- Cualquier persona con Node 20+ y Python 3.12+ puede correr el proyecto localmente.

**Negativas:**
- **Acoplamiento a Cloudflare** para API y hosting. Si en el futuro queremos migrar a otro proveedor, hay que reescribir bindings específicos (R2, KV, D1).
- **Astro no es ideal para apps altamente interactivas**. Si el observatorio evoluciona hacia un dashboard en tiempo real (no planeado en Fase 0), podría convenir migrar a Next.js o Remix. Lo dejamos explícito como riesgo.
- **Dos lenguajes** (TS + Python) aumentan el contexto mental del equipo. Se mitiga con interfaces claras: Python produce Parquet/JSON, TS los consume; no hay llamadas directas entre runtimes.
- **Sin base de datos relacional** en Fase 0. Si los datos etiquetados crecen más allá de ~100k registros y se necesitan joins complejos, habrá que añadir D1 (SQLite en Workers) o Postgres externo. Documentado como seguimiento.

## Alternativas consideradas

### Para web
- **Next.js 15**: descartado por overhead de runtime para un sitio mayoritariamente estático. Si la web evoluciona a dashboard, se revisita.
- **SvelteKit**: sólido, pero menos ecosistema en verificación de datos / visualización que React.
- **Hugo / Eleventy**: muy rápidos, pero la flexibilidad de Astro (islas) pesó más.

### Para API
- **Vercel Edge Functions**: equivalente funcional a Workers, pero ya estábamos alineados con Cloudflare para Pages.
- **FastAPI en VPS**: más flexible pero introduce un servidor que mantener y monitorear.
- **Supabase Edge Functions**: demasiado acoplamiento a su ecosistema.

### Para pipeline
- **Node.js + TypeScript**: mantendría un solo lenguaje, pero Python tiene mejor ecosistema para NLP (spaCy, transformers, sentence-transformers).
- **Go**: más rápido y monolítico, pero el ecosistema de análisis es pobre comparado con Python.

## Referencias

- [Astro Islands Architecture](https://docs.astro.build/en/concepts/islands/)
- [Cloudflare Workers docs](https://developers.cloudflare.com/workers/)
- [uv documentation](https://docs.astral.sh/uv/)
- [Hono framework](https://hono.dev/)

---

Cualquier cambio de stack posterior requiere un ADR nuevo que reemplace este, con justificación de qué cambió en el contexto.
