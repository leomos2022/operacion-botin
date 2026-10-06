# Operación Botín

> Observatorio educativo sobre bots y desinformación en Colombia.
> "Hay cuentas que no duermen. Y están hablando contigo."

## Stack

- **Web**: Astro 5 + Tailwind CSS 4 + React 19 (apps/web)
- **API**: Cloudflare Worker + Hono (apps/api)
- **Pipeline de datos**: Python 3.12 + uv (pipeline/)
- **Paquete compartido**: tipos TS + datasets JSON/Parquet (packages/shared)

## Estructura

    operacion-botin/
    ├── apps/
    │   ├── web/      → sitio estático (Astro 5 + Tailwind)
    │   └── api/      → API en Cloudflare Worker (Hono)
    ├── pipeline/     → extracción, features, RAG (Python 3.12)
    ├── packages/
    │   └── shared/   → tipos TS + datos (JSON/Parquet)
    ├── docs/adr/     → Architecture Decision Records
    ├── .github/workflows/ci.yml
    ├── AGENT_RULES.md  ← REGLAS DEL PROYECTO (leer al iniciar sesión)
    ├── TASKS.md        ← Checklist de fases
    └── README.md

## Quickstart

### Requisitos

- Node.js 20+ (recomendado 22 LTS)
- Python 3.12+ y uv (https://docs.astral.sh/uv/)
- Cuenta de Cloudflare (gratis) para deploy

### 1. Clonar e instalar

    git clone <repo-url> operacion-botin
    cd operacion-botin
    cp .env.example .env

    # Web
    cd apps/web && npm install && cd ../..

    # API
    cd apps/api && npm install && cd ..

### 2. Desarrollo local

    # Web (http://localhost:4321)
    cd apps/web && npm run dev

    # API (http://localhost:8787) — en otra terminal
    cd apps/api && npx wrangler dev

    # Pipeline
    cd pipeline && uv sync && uv run python -m src.extract

### 3. Build de producción

    cd apps/web && npm run build
    cd apps/api && npm run typecheck

## Deploy

### Web → Cloudflare Pages

**Opción A — Conectando GitHub (recomendado para deploy automático):**

1. Sube el repo a GitHub.
2. Entra a Cloudflare Pages → "Create a project" → "Connect to Git".
3. Selecciona el repo `operacion-botin`.
4. Configura:
   - Framework preset: Astro
   - Build command: `cd apps/web && npm install && npm run build`
   - Build output directory: `apps/web/dist`
   - Node version: 22 (env var NODE_VERSION=22)
5. "Save and Deploy". El primer deploy tarda ~2 min.
6. Cada `git push` a `main` despliega automáticamente.

**Opción B — Con Wrangler CLI (deploy manual):**

    cd apps/web
    npx wrangler pages deploy dist --project-name=operacion-botin

### API → Cloudflare Workers

    # 1. Autenticarse con Cloudflare (una sola vez)
    cd apps/api
    npx wrangler login

    # 2. Configurar account_id
    export CLOUDFLARE_ACCOUNT_ID=tu_account_id

    # 3. Deploy
    npx wrangler deploy

La API queda en `https://operacion-botin-api.<tu-subdomain>.workers.dev`.

**Smoke test del API en producción:**

    curl https://operacion-botin-api.<tu-subdomain>.workers.dev/api/v1/health
    # → {"status":"ok","env":"production","ts":"..."}

### Configurar dominio personalizado (opcional)

1. Web: en Cloudflare Pages → "Custom domains" → añade `operacionbotin.co`.
2. API: en Cloudflare Workers → "Triggers" → "Custom domains" → añade `api.operacionbotin.co`.
3. Actualiza `site` en `apps/web/astro.config.mjs` y el `Sitemap:` en `apps/web/public/robots.txt`.

## Smoke test post-deploy

    # 1. Sitemap accesible
    curl https://<tu-dominio>/sitemap-index.xml

    # 2. Robots.txt accesible
    curl https://<tu-dominio>/robots.txt

    # 3. Health del API
    curl https://<tu-api-dominio>/api/v1/health

    # 4. Páginas sin 404
    for ruta in / /casos /la-industria /metodologia /verifica /precios /ui; do
      echo -n "$ruta: "
      curl -o /dev/null -s -w "%{http_code}\n" "https://<tu-dominio>$ruta"
    done

## Reglas del proyecto

Lee AGENT_RULES.md antes de cualquier cambio.
Las reglas editoriales y de commits son vinculantes.

## Decisiones arquitectónicas

Las decisiones significativas se documentan en docs/adr/:

- ADR-0001: Selección de stack
- ADR-0002: Categorización de cuentas
- ADR-0003: Modelo freemium de 3 capas

## Progreso

Consulta TASKS.md para ver el estado de cada fase.

## Autor

**Leonardo Mosquera Rodríguez** — Ingeniero de Software, Bogotá, Colombia.
Email: leomoslab@gmail.com

## Licencia

- Código: MIT
- Contenido editorial: Creative Commons BY-SA 4.0
- Datos: atribución por ficha (ver packages/shared/data/)
