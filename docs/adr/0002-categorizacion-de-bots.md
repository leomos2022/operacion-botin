# ADR-0002: Categorización de cuentas — 4 categorías técnicas

- **Estado**: Aceptado
- **Fecha**: 2026-10-05
- **Decisor**: equipo editorial Operación Botín

## Contexto

El observatorio necesita un sistema de categorización de cuentas que sea:

1. **Técnicamente fundado**: basado en comportamiento observable, no en opiniones políticas.
2. **Resistente al abuso**: no se puede usar para etiquetar como "bot" a quien simplemente disiente.
3. **Comprensible para ciudadanía**: si el público no entiende las categorías, no sirven.
4. **Útil para investigación**: debe permitir análisis agregado (¿cuántos bots?, ¿cuántos trolls?).
5. **Diferenciada**: el debate público usa "bot" como cajón de sastre para todo lo anterior. Eso es exactamente el problema que queremos combatir.

El debate público en Colombia (y la región) usa "bot" de forma vaga: para descalificar al contrario, para referirse a cuentas falsas, para describir trolls pagados, para nombrar cualquier operación coordinada. Esta ambigüedad beneficia a quien quiere confundir, no a quien quiere entender.

## Decisión

Adoptamos **4 categorías técnicas mutuamente distinguibles**, definidas por criterios observables, no políticos:

| Categoría | Tipo de criterio | Definición corta |
|-----------|------------------|------------------|
| **Bot** | Técnico | Cuenta con comportamiento automatizado demostrable. |
| **Troll** | Conductual | Humano que hostiga, polariza o desvía conversaciones de forma sostenida. |
| **Cuenta falsa** | Identidad | Identidad fabricada (foto robada/generada, bio inconsistente, sin huella verificable). |
| **Operador coordinado** | Grupo | Conjunto de cuentas (≥5) en sincronía que sugiere dirección central. |

Una cuenta puede recibir **varias etiquetas simultáneas** (p. ej. "bot" + "cuenta falsa"). En ese caso, se documentan ambas y se explica la relación.

Cada etiqueta incluye: **grado de confianza** entre 0 y 1 (no se publica con <0.7), **fecha de etiquetado** (ISO 8601), **fuente del etiquetado** (URL o referencia al informe) y **notas** del revisor humano.

## Regla editorial fundamental

**"Bot" no es persona que discrepa.** Esta regla se incluye en `AGENT_RULES.md` §4.2 y es la línea roja del observatorio. La categoría bot requiere evidencia técnica de automatización, no opinión sobre el contenido de lo que dice.

## Consecuencias

**Positivas:**
- El observatorio puede distinguir lo que el debate público confunde. Eso es su valor agregado.
- Las categorías son útiles para análisis agregado: se pueden contar bots vs trolls vs cuentas falsas por separado.
- La regla editorial protege al observatorio de ser usado como herramienta de deslegitimación de voces críticas.
- Ciudadanía puede entender las categorías con definiciones cortas; el detalle técnico vive en metodología.

**Negativas:**
- **"Operador coordinado" requiere identificación de grupo** (≥5 cuentas). Más costoso que etiquetar cuentas individuales; reduce el volumen de etiquetas de este tipo.
- **"Troll" es la categoría más subjetiva** y la que más revisión humana exige. Hay riesgo de inconsistencia entre revisores. Se mitiga con doble revisión en discrepancia.
- **No capturamos matices**. Una cuenta puede ser bot en algunos momentos y operada manualmente en otros. La etiqueta es una instantánea, no una propiedad permanente. Se documenta la fecha.
- **La categoría "humano verificado" no es una etiqueta de cuenta**; es la ausencia de las anteriores. Se mantiene en el enum por consistencia pero no se "otorga" como certificado.

## Alternativas consideradas

### Una sola categoría "cuenta sospechosa"
- **Descartada**: pierde toda la información diferenciadora. No permite responder "¿cuántos bots vs trolls?".

### Espectro de confianza (0-100) sin categorías
- **Descartada**: poco comprensible para ciudadanía. Una etiqueta cualitativa es más comunicable.

### Más categorías (bot, troll, cuenta falsa, operador coordinado, astroturf, sockpuppet, cyborg, cyborg coordinado, ...)
- **Descartada por ahora**: la granularidad añadida no compensa el costo cognitivo. Si en el futuro hay datos suficientes para justificar subcategorías, se añaden sin romper las 4 existentes.

### Modelo de Botometer / BotSentinel (score único)
- **Descartada**: dependemos de un tercero, opaco, y no diferenciado. El observatorio necesita definir sus propios criterios.

## Implementación técnica

Las categorías se definen en `packages/shared/types/index.ts` como `CategoriaCuenta`:

- `'bot'`
- `'troll'`
- `'cuenta_falsa'`
- `'operador_coordinado'`
- `'humano_verificado'`
- `'sin_clasificar'`

El pipeline produce etiquetas candidatas; un revisor humano valida; solo se publican etiquetas con confianza ≥0.7 y doble confirmación si hay discrepancia.

## Referencias

- Documento de metodología: `/metodología` (sección 01 Definiciones)
- Reglas editoriales: `AGENT_RULES.md` §4
- Tipos TS: `packages/shared/types/index.ts`

---

Cualquier cambio a las categorías (añadir, renombrar, eliminar) requiere un ADR nuevo. Las 4 categorías son un compromiso editorial del observatorio; cambiarlas silenciosamente rompería la confianza acumulada.
