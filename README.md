# Operación Botín

> Observatorio educativo sobre bots y desinformación en Colombia.
> "Hay cuentas que no duermen. Y están hablando contigo."

## Stack

- **Web**: Astro 5 + Tailwind CSS 4 + React 19 (apps/web)
- **API**: Cloudflare Worker + Hono (apps/api)
- **Pipeline de datos**: Python 3.12 + uv (pipeline/)
- **Paquete compartido**: tipos TS + datasets JSON/Parquet (packages/shared)

## Estructura

```
operacion-botin/
├── apps/
│   ├── web/      → sitio estático (Astro 5 + Tailwind)
│   └── api/      → API en Cloudflare Worker (Hono)
├── pipeline/     → extracción, features, RAG (Python 3.12)
├── packages/
│   └── shared/   → tipos TS + datos (JSON/Parquet)
├── .github/workflows/ci.yml
├── AGENT_RULES.md  ← REGLAS DEL PROYECTO (leer al iniciar sesión)
├── TASKS.md        ← Checklist de fases
└── README.md
```

## Quickstart

### Requisitos

- Node.js 20+ (recomendado 22 LTS)
- Python 3.12+ y [uv](https://docs.astral.sh/uv/)
- Cuenta de Cloudflare (para deploy de API)

### 1. Clonar e instalar

```bash
git clone <repo-url> operacion-botin
cd operacion-botin
cp .env.example .env   # rellena tus credenciales
```

### 2. Web (Astro)

```bash
cd apps/web
npm install
npm run dev      # http://localhost:4321
npm run build    # genera dist/
```

### 3. API (Cloudflare Worker)

```bash
cd apps/api
npm install
npx wrangler dev   # http://localhost:8787
# healthcheck: GET http://localhost:8787/api/v1/health
```

### 4. Pipeline (Python)

```bash
cd pipeline
uv sync
uv run python -m src.extract
```

## Reglas del proyecto

Lee [`AGENT_RULES.md`](./AGENT_RULES.md) antes de cualquier cambio.
Las reglas editoriales y de commits son vinculantes.

## Progreso

Consulta [`TASKS.md`](./TASKS.md) para ver el estado de cada fase.

## Licencia

Código: MIT. Contenido editorial: Creative Commons BY-SA 4.0.
Datos: ver ficha de cada dataset (siempre con atribución).
