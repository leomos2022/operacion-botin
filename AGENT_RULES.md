# AGENT_RULES.md — Reglas del proyecto "Operación Botín"

> **Lectura obligatoria al inicio de cada sesión.**
> Este archivo define el stack, las convenciones y las reglas editoriales
> del proyecto. Cualquier desviación debe justificarse explícitamente.

## 1. Identidad del proyecto

**Operación Botín** es un observatorio educativo sobre bots y desinformación
en Colombia. El tono editorial es **periodístico, documentado y sereno**:
no sensacionalista, no alarmista, no conspirativo. El público objetivo es
ciudadanía interesada en entender cómo opera la desinformación, periodistas,
educadores y equipos de verificación.

## 2. Stack técnico (vinculante)

| Capa            | Tecnología                                |
|-----------------|-------------------------------------------|
| Web             | Astro 5 + Tailwind CSS 4 + React 19       |
| API             | Cloudflare Worker + Hono + TypeScript     |
| Pipeline datos  | Python 3.12 + uv                          |
| Compartido      | TypeScript types + JSON/Parquet           |
| Deploy web      | Cloudflare Pages (estático)               |
| Deploy API      | Cloudflare Workers                        |
| CI              | GitHub Actions                            |

**TypeScript strict** en `apps/`, `packages/`. Python con `ruff` + `mypy --strict`.

## 3. Design tokens (no cambiar sin justificación)

```css
--bg:      #0E1116;   /* fondo principal */
--surface: #161B22;   /* tarjetas, header, footer */
--rojo:    #E5484D;   /* alertas, bots detectados */
--verde:   #3FB68B;   /* verificado, OK */
--ambar:   #F5A524;   /* advertencia, pendiente */
--texto:   #E6EDF3;   /* texto principal */
--muted:   #9BA7B4;   /* texto secundario */
```

**Fuentes**:
- Display: **Archivo Black** (titulares, hero)
- Body: **Inter** (cuerpo, navegación)
- Datos: **JetBrains Mono** (tablas, métricas, JSON)

## 4. Reglas editoriales (vinculantes)

1. **Nada de datos sin fuente.** Todo número, gráfica o afirmación factual
   debe llevar atribución verificable. Si no hay fuente, no se publica.
2. **"Bot" ≠ persona que discrepa.** La categoría "bot" se reserva para
   cuentas con comportamiento automatizado demostrable (heurística + revisión
   humana). Nunca etiquetar como bot a alguien solo por disentir.
3. **Diferenciar bot, troll, cuenta falsa y operador coordinado.** Son
   categorías distintas con definiciones en `docs/glosario.md` (fase posterior).
4. **Privacidad: no doxxing.** Mostrar identificadores seudonimizados
   (p. ej. `@cuenta***`) salvo cuando la cuenta haya sido identificada
   públicamente por una autoridad o investigación periodística firmada.
5. **Tono: documentar, no acusar.** Describir el comportamiento observado,
   no las intenciones inferidas, salvo cuando un informe las atribuya.
6. **Corrección visible.** Toda corrección posterior se marca con fecha y
   motivo. Nunca se borra silenciosamente.
7. **Colombia primero.** El foco geográfico es Colombia. Casos extranjeros
   solo como comparativo metodológico, claramente etiquetados.

## 5. Convención de commits (Conventional Commits)

Formato: `<tipo>(<alcance>): <descripción>`

**Tipos permitidos**:
- `feat`     nueva funcionalidad
- `fix`      corrección de bug
- `docs`     cambios en documentación (README, TASKS, AGENT_RULES, ADRs)
- `style`    formato, sin cambio de código
- `refactor` reestructuración sin cambio de comportamiento
- `test`     añadir o corregir tests
- `chore`    tooling, deps, CI, tareas de mantenimiento
- `data`     (extensión propia) cambios en datasets de packages/shared/data

**Alcances típicos**: `web`, `api`, `pipeline`, `shared`, `ci`, `docs`, `design`.

**Ejemplos**:
```
feat(web): hero scrollytelling en home
fix(api): manejo de CORS en /api/v1/health
docs: actualiza TASKS.md con fase 0.2 completada
data(shared): añade dataset inicial de cuentas etiquetadas
chore(ci): añade job de lint para pipeline
```

- Commits **atómicos**: una idea lógica por commit.
- Mensaje en **minúscula**, descripción en imperativo.
- Si cierra un issue: `Closes #123` en el cuerpo.

## 6. Estructura de archivos (respetar)

```
apps/
  web/    → páginas, layouts, componentes, estilos
  api/    → rutas Hono, handlers
pipeline/
  src/extract/   → recolección de datos de plataformas
  src/features/  → transformaciones, métricas, etiquetas
  src/rag/       → indexación semántica, retrieval
packages/shared/
  types/   → interfaces TS compartidas
  data/    → datasets versionados (JSON/Parquet)
```

- No crear carpetas "utils" genéricas. Nombrar por dominio.
- No duplicar lógica entre apps: si se usa en 2+ sitios, vive en `packages/shared`.

## 7. Flujo por tarea (sesión)

1. Leer `AGENT_RULES.md` y `TASKS.md` al inicio.
2. Continuar con la tarea marcada como EN CURSO.
3. Al terminar:
   - commit atómico siguiendo convención,
   - marcar tarea como HECHA en `TASKS.md`,
   - exportar con `git bundle create backup.bundle --all` (o según canal),
   - resumen de máximo 5 líneas.
4. **No avanzar a la siguiente tarea sin confirmación explícita del usuario.**

## 8. Calidad mínima

- Lint sin errores antes de commit (`npm run lint`, `ruff check .`).
- Build de `apps/web` debe pasar sin errores.
- Tipos TS sin errores (`tsc --noEmit`).
- No commitear `console.log` de debug. Si es necesario, usar logger nombrado.

## 9. Documentación de decisiones (ADRs)

Decisiones arquitectónicas significativas se documentan en
`docs/adr/NNNN-titulo.md` (formato MADR simplificado). Se introducen en
fase 0.7.

## 10. Idioma

- Código, comentarios y docs internos: **español** (excepto identificadores
  técnicos estándar en inglés: `healthcheck`, `handler`, `middleware`).
- Contenido editorial publicado: **español (Colombia)**.
