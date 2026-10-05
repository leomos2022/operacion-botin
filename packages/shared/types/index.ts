/**
 * Operación Botín — tipos compartidos
 *
 * Interfaces TS usadas tanto por apps/web como por apps/api.
 * El pipeline de Python genera datos que se publican en packages/shared/data
 * y se consumen vía estos tipos.
 */

// ─────────────────────────────────────────────────────────────
// Categorías de cuenta (ver AGENT_RULES.md §4)
// ─────────────────────────────────────────────────────────────

export type CategoriaCuenta =
  | 'bot'
  | 'troll'
  | 'cuenta_falsa'
  | 'operador_coordinado'
  | 'humano_verificado'
  | 'sin_clasificar';

export interface CuentaEtiquetada {
  /** Identificador seudonimizado — ver regla de privacidad §4.4 */
  idSeudonimo: string;
  plataforma: Plataforma;
  categoria: CategoriaCuenta;
  /** Confianza de la etiqueta en [0, 1] */
  confianza: number;
  fechaEtiquetado: string; // ISO 8601
  fuenteEtiquetado: string; // URL o referencia al informe
  notas?: string;
}

// ─────────────────────────────────────────────────────────────
// Plataformas soportadas
// ─────────────────────────────────────────────────────────────

export type Plataforma =
  | 'twitter'
  | 'telegram'
  | 'bluesky'
  | 'facebook'
  | 'tiktok'
  | 'instagram'
  | 'otra';

// ─────────────────────────────────────────────────────────────
// Casos documentados
// ─────────────────────────────────────────────────────────────

export interface Caso {
  slug: string;
  titulo: string;
  resumen: string;
  fechaInicio: string; // ISO 8601
  fechaCierre?: string;
  plataformas: Plataforma[];
  etiquetas: string[];
  estado: 'borrador' | 'publicado' | 'actualizado' | 'archivado';
  fuentes: Fuente[];
  metricasClave?: MetricaClave[];
}

export interface Fuente {
  /** Tipo: informe propio, medio, autoridad, dataset público... */
  tipo: 'informe_propio' | 'medio' | 'autoridad' | 'academico' | 'dataset' | 'otro';
  url: string;
  titulo: string;
  autor?: string;
  fechaConsulta: string; // ISO 8601
}

export interface MetricaClave {
  etiqueta: string;
  valor: string;
  unidad?: string;
  fuente: string; // URL o referencia
}

// ─────────────────────────────────────────────────────────────
// API — respuestas
// ─────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'down';
  env?: string;
  ts: string;
}

export interface ApiError {
  error: string;
  message?: string;
  path?: string;
}
