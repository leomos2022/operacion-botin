# @operacion-botin/api

API de Operación Botín — Cloudflare Worker + Hono.

## Cómo correrlo

### Requisitos

- Node.js 20+
- Cuenta de Cloudflare (para deploy)
- `wrangler` (se instala como dependencia del paquete)

### Desarrollo local

```bash
cd apps/api
npm install
npm run dev
```

El worker queda disponible en `http://localhost:8787`.

**Smoke test:**

```bash
curl http://localhost:8787/api/v1/health
# → {"status":"ok","env":"development","ts":"2026-..."}
```

### Typecheck

```bash
npm run typecheck
```

### Deploy

```bash
# 1. Autentícate con Cloudflare (una sola vez)
npx wrangler login

# 2. Configura tu account_id en wrangler.toml o vía variable de entorno
export CLOUDFLARE_ACCOUNT_ID=tu_account_id

# 3. Despliega
npm run deploy
```

## Estructura

```
apps/api/
├── src/
│   └── index.ts        → router Hono, endpoint /api/v1/health
├── wrangler.toml       → config del worker
├── tsconfig.json
└── package.json
```

## Rutas (fase 0.1)

| Método | Ruta              | Descripción                          |
|--------|-------------------|--------------------------------------|
| GET    | `/api/v1/health`  | Healthcheck del servicio             |
| GET    | `/`               | Redirección a `/api/v1/health`       |

Las rutas de casos, métricas y búsqueda se añaden en fases posteriores
(ver `TASKS.md` en la raíz del monorepo).

## Variables de entorno

| Variable      | Descripción                  | Ejemplo         |
|---------------|------------------------------|-----------------|
| `CF_ENV`      | Entorno de ejecución          | `development`   |

Secretos (R2, KV, D1) se configuran vía `wrangler secret put` en su fase.
