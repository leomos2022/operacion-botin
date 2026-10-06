# ADR-0003: Modelo freemium de 3 capas para monetización

- **Estado**: Aceptado
- **Fecha**: 2026-10-05
- **Decisor**: equipo Operación Botín

## Contexto

El observatorio necesita sostenibilidad económica a medio plazo. Las opciones habituales son:

1. **Donaciones / grants** (estilo Bellingcat) — valioso pero intermitente.
2. **Patrocinio corporativo** — peligroso para credibilidad editorial.
3. **Pago por contenido (paywall total)** — rompe la promesa de metodología abierta.
4. **Freemium con capas** — combina acceso ciudadano libre con valor comercial para profesionales.

El observatorio tiene una **promesa editorial explícita** que no puede romper: metodología abierta, datos con fuente, sin conflictos de interés ocultos. Si de repente pusiéramos los casos detrás de un paywall, perderíamos la confianza que es justo lo que da valor a la investigación.

Sin embargo, hay audiencias con capacidad de pago que necesitan más de lo que la versión gratuita puede ofrecer:
- **Redacciones y medios** que necesitan datos antes que sus competidores
- **Equipos de compliance y reputación** de empresas
- **Académicos** que requieren datasets exportables
- **ONGs y observatorios internacionales**
- **Gobiernos y organismos electorales** (con declaración de conflicto)

Hay tensión: el modelo debe capturar valor de estas audiencias sin sacrificar el acceso ciudadano libre.

## Decisión

Adoptamos un **modelo freemium de 3 capas** con una regla rectora:

> **Lo que protege a la ciudadanía es gratis. Lo que tiene valor comercial es premium. Nunca se mezcla.**

### Capa 1 — Ciudadana (gratis, siempre)

| Recurso | Disponibilidad |
|---------|----------------|
| Metodología completa | Abierta, CC BY-SA 4.0 |
| Home, scrollytelling, hero | Público |
| Casos: resumen, plataformas, métricas clave | Público |
| Verifica (formulario de reporte) | Siempre gratis (la voz ciudadana es el insumo) |
| Newsletter mensual | Gratis |
| Glosario y definiciones | Público |

### Capa 2 — Profesional (suscripción mensual)

| Recurso | Disponibilidad |
|---------|----------------|
| Expediente completo de casos publicados | Premium |
| Cuentas seudonimizadas con etiquetas y confianza | Premium |
| Capturas y evidencia primaria | Premium |
| Newsletter semanal + alertas tempranas | Premium |
| Búsqueda avanzada con filtros | Premium |

### Capa 3 — Organización (suscripción anual)

| Recurso | Disponibilidad |
|---------|----------------|
| API con endpoints `/casos`, `/cuentas`, `/datasets` | Premium |
| Datos exportables (Parquet, JSON) | Premium |
| Webhooks de alertas | Premium |
| Acceso a informes exclusivos | Premium |
| Soporte y SLA | Premium |

### Planes y precios

Los precios se definen en `/precios`. La política general:

- **Gratis**: para todo, sin límite de cuenta
- **Profesional**: suscripción mensual individual, precio accesible (~USD 15-25/mes estimado)
- **Organización**: suscripción anual por equipo, precio según uso (~USD 500-2000/año estimado)

Los precios finales se publican en Fase 0.8 junto con la integración de pagos.

### Reglas no negociables

1. **Lo ciudadano nunca va detrás de paywall.** Si una información protege a alguien de una operación de desinformación, es gratis.
2. **Verifica es siempre gratis.** La voz ciudadana no se cobra.
3. **Metodología es siempre abierta.** Si no entiendes cómo etiquetamos, no puedes confiar.
4. **Todo patrocinador o cliente se declara públicamente.** No hay relaciones comerciales ocultas.
5. **No vendemos datos personales identificables.** Solo seudonimizados, según regla editorial §4.4.
6. **No aceptamos patrocinio de actores políticos o gubernamentales en periodo electoral.** Conflicto demasiado directo.

## Consecuencias

**Positivas:**
- Modelo sostenible sin sacrificar la promesa editorial.
- Alinea incentivos: mejor investigación → más audiencia premium → más recursos para investigación.
- Ciudadanía accede a lo esencial; profesionales pagan por el trabajo extra de estructuración y datos.
- API se vuelve producto, no solo infraestructura.

**Negativas:**
- **Doble mantenimiento**: hay que mantener capa gratuita y premium en paralelo. Se mitiga con el componente `PremiumGate.astro` (marca visual, no bloquea).
- **Riesgo de captura**: si un cliente grande presiona para cambiar metodología, hay que resistir. Documentado como riesgo.
- **Costo de infraestructura de pagos**: requiere integrar Stripe / similar. Se añade en Fase 0.8.
- **Fricción legal**: términos de servicio, privacidad, facturación. Requiere asesoría legal antes del lanzamiento comercial.

## Alternativas consideradas

### Paywall total (todo paga)
- **Descartada**: rompe la promesa editorial y reduce alcance ciudadano.

### Solo donaciones / grants
- **Descartada como única fuente**: intermitente, no escalable. Se mantiene como complemento.

### Patrocinio corporativo con visibilidad
- **Descartada** para el núcleo editorial: el conflicto de interés es demasiado directo. Podría aceptarse para eventos puntuales con transparencia total, pero no para financiar la operación continua.

### API pública gratis para todos
- **Descartada**: el costo de infraestructura lo pagamos nosotros. La API con datos etiquetados tiene valor comercial claro; cobrar por ella no rompe el acceso ciudadano a los resúmenes.

### Vender datos a terceros sin transparencia
- **Descartada**: viola la regla editorial de transparencia. Todo cliente se declara.

## Implementación técnica

- **Componente `PremiumGate.astro`**: wrapper que muestra contenido con badge "Premium" y CTA a `/precios`. **No bloquea el acceso** en Fase 0 — solo marca visualmente qué será premium.
- **Tipos en `packages/shared`**: el tipo `Caso` ya tiene campo `estado` (`borrador` | `publicado` | `actualizado` | `archivado`). Se añade `nivelAcceso` (`publico` | `profesional` | `organizacion`) cuando se implementen los endpoints premium.
- **API en `apps/api`**: `/api/v1/health` es público. Los endpoints `/api/v1/casos`, `/api/v1/cuentas`, `/api/v1/datasets` requerirán API key (middleware Hono). Se implementa en Fase 1.
- **Página `/precios`**: muestra los 3 planes. Se crea en esta fase (0.7).

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cliente grande presiona para cambiar metodología | Media | Crítico | Editorial independiente por contrato; ADR-0002 es vinculante. |
| Filtración de datos premium | Baja | Alto | Seudonimización obligatoria; datos crudos viven solo en el pipeline. |
| Confusión sobre qué es gratis vs premium | Alta | Medio | Política clara en `/precios`; componente `PremiumGate` visible. |
| Baja conversión a premium | Media | Medio | Iteración de planes según feedback; mantener valor claro. |

## Referencias

- Reglas editoriales: `AGENT_RULES.md` §4 (especialmente §4.6 transparencia)
- Componente: `apps/web/src/components/PremiumGate.astro`
- Página de precios: `apps/web/src/pages/precios.astro`
- Tipos compartidos: `packages/shared/types/index.ts`

---

Este ADR no se reemplaza fácilmente. Cualquier cambio al modelo freemium requiere un ADR nuevo y debe ser comunicado explícitamente a la audiencia (regla editorial §4.6: corrección visible).
