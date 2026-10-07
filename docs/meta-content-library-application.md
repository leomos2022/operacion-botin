# Carta de intención — Meta Content Library

> Plantilla para aplicación a Meta Content Library.
> Adapta los datos antes de enviar a
> https://www.facebook.com/form_content_library/researcher

## Información del solicitante

- **Nombre:** Leonardo Mosquera Rodríguez
- **Email:** leomoslab@gmail.com
- **Rol:** Investigador independiente · Ingeniero de Software
- **Ubicación:** Bogotá, Colombia
- **Proyecto:** Operación Botín
- **Sitio:** https://operacion-botin.pages.dev
- **Repo:** https://github.com/leomos2022/operacion-botin

## Resumen del proyecto

Operación Botín es un observatorio educativo independiente que documenta cómo operan los bots y la desinformación en Colombia. Nació en octubre de 2026 como respuesta a la circulación de contenido manipulado en redes sociales durante el ciclo electoral colombiano.

Tres diferenciadores:

1. **Metodología abierta y verificable.** Publicamos cómo etiquetamos (bot, troll, cuenta falsa, operador coordinado), qué heurísticas usamos, qué confianza exigimos (≥0.7) y qué limitaciones tiene el análisis. CC BY-SA 4.0.

2. **Sin conflictos de interés.** No aceptamos patrocinio político ni gubernamental en periodo electoral. No vendemos datos personales identificables. Modelo freemium: capa ciudadana gratis, capa profesional/organización de pago.

3. **Transparencia editorial.** Toda corrección visible con fecha y motivo. Reportamos ausencia de evidencia como hallazgo. Regla fundamental: "Bot" no es persona que discrepa.

Hasta la fecha: 157 posts públicos de Bluesky capturados, primer caso documentado con datos reales en https://operacion-botin.pages.dev/casos/primera-extraccion

## Caso de uso

### Objetivo

Identificar y categorizar cuentas públicas en Facebook Pages e Instagram que muestren patrones automatizados o coordinados durante el ciclo electoral colombiano 2026-2027.

### Contenido a consultar

- Posts públicos de Facebook Pages con audiencia colombiana sobre elecciones, figuras políticas y términos asociados a desinformación
- Posts públicos de cuentas de creadores de Instagram públicas con temática política en Colombia
- Comentarios públicos en posts relevantes para análisis de coordinación

### Metodología

3 familias de heurísticas ya publicadas:

1. **Señales temporales:** distribución de horarios, intervalos mecánicos, picos sincronizados
2. **Señales de contenido:** repetición de textos, hashtags coordinados, plantillas
3. **Señales de grafo:** clusters densos sin conexión externa, respuesta coordinada

Todo etiquetado pasa revisión humana. Confianza ≥0.7 para publicación.

### Datos a extraer

Solo campos públicos de Meta Content Library:
- Texto del post o comentario
- Timestamp de publicación
- Identificador de cuenta (seudonimizado antes de publicar)
- Métricas agregadas (likes, shares, comments)
- URL pública

**No solicitamos** datos privados, mensajes directos, ni información personal de usuarios.

## Plan de publicación

1. **Seudonimización obligatoria** antes de cualquier publicación (regla §4.4)
2. **Medios públicos reconocidos** son la única excepción (medios colombianos oficiales)
3. **Cifra con fuente** siempre (regla §4.1)
4. **Corrección visible** (regla §4.6)
5. **Licencias:** Código MIT, contenido CC BY-SA 4.0

## Beneficio público

La desinformación en Colombia durante ciclos electorales ha sido documentada por Universidad de los Andes, Fundación Karisma y otros. Pero no existe un observatorio independiente con metodología abierta multicanal.

Con acceso a Meta Content Library, el observatorio podría:

1. Detectar operaciones de desinformación que se mueven sin monitoreo público en FB e Instagram
2. Publicar análisis comparativos multicanal (Bluesky + Telegram + FB + Instagram)
3. Proveer a ciudadanía, periodistas y educadores herramientas concretas
4. Ofrecer a redacciones colombianas datos verificables

## Compromisos

1. Uso exclusivo para los fines descritos
2. No compartir credenciales ni datos
3. Cumplir términos de Meta Content Library
4. Publicación transparente, metodología abierta
5. Reportar a Meta cualquier uso indebido
6. Auditoría disponible si Meta lo solicita

## Documentación adjunta

- Sitio: https://operacion-botin.pages.dev
- Repo: https://github.com/leomos2022/operacion-botin
- Metodología: https://operacion-botin.pages.dev/metodologia
- Primer caso: https://operacion-botin.pages.dev/casos/primera-extraccion
- ADRs: https://github.com/leomos2022/operacion-botin/tree/main/docs/adr

## Contacto

Leonardo Mosquera Rodríguez
leomoslab@gmail.com
Bogotá, Colombia

---

## Notas para el envío

1. Adapta los datos antes de enviar
2. Envío en https://www.facebook.com/form_content_library/researcher
3. Revisión típica: 2-4 semanas
4. Si piden afiliación institucional, menciona que eres investigador independiente con proyecto público
