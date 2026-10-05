# Datos compartidos — Operación Botín

Datasets versionados consumidos por la web y la API.

## Reglas

1. **Todo dataset lleva una ficha** (`<nombre>.meta.json`) con:
   - fuente original (URL),
   - fecha de descarga,
   - licencia,
   - método de transformación,
   - responsable.
2. **No se publican identificadores personales** sin seudonimizar
   (ver `AGENT_RULES.md` §4.4).
3. Los archivos Parquet se ignoran en git (ver `.gitignore`); se distribuyen
   vía R2 o release attachments.
4. Los JSON pequeños (<1 MB) sí se versionan en git.

## Estado

Fase 0.1 — vacío a propósito. Los primeros datasets se incorporan en Fase 1.
