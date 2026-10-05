/**
 * Operación Botín — API (Cloudflare Worker + Hono)
 *
 * Punto de entrada del worker. Define el router raíz y monta las rutas
 * bajo /api/v1/*. Por ahora solo expone /health; las rutas de casos,
 * métricas y búsqueda se añaden en fases posteriores.
 */

import { Hono } from 'hono';

// Tipos del entorno de ejecución del Worker (bindings de Cloudflare).
// Por ahora solo variables no secretas; añadiremos R2, KV, D1 en su fase.
export interface Env {
  CF_ENV: string;
}

const app = new Hono<{ Bindings: Env }>();

/**
 * Healthcheck.
 * GET /api/v1/health → 200 {"status":"ok","env":"...","ts":"..."}
 *
 * No requiere autenticación. Pensado para smoke-tests post-deploy
 * y para que el frontend pueda verificar disponibilidad.
 */
app.get('/api/v1/health', (c) => {
  return c.json({
    status: 'ok',
    env: c.env.CF_ENV ?? 'unknown',
    ts: new Date().toISOString(),
  });
});

/**
 * Ruta raíz — redirige a /api/v1/health para que cualquier GET /
 * devuelva algo útil en lugar de 404.
 */
app.get('/', (c) => c.redirect('/api/v1/health'));

/**
 * 404 centralizado con formato JSON consistente.
 */
app.notFound((c) => {
  return c.json({ error: 'not_found', path: c.req.path }, 404);
});

/**
 * Manejador de errores global. Nunca filtrar stack traces en producción.
 */
app.onError((err, c) => {
  console.error('unhandled_error', err);
  const message =
    c.env?.CF_ENV === 'production'
      ? 'internal_error'
      : (err as Error).message;
  return c.json({ error: 'internal', message }, 500);
});

export default app;
