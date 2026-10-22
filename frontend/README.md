# PHIS · Evidence UI demo

Frontend autónomo para una sola investigación longitudinal de energía. **Todo el contenido de datos es sintético**. La rama ejecuta funciones locales deterministas y no afirma conectar Zetaris, Meterless, Nemotron ni el backend PHIS.

## Ejecutar

Requiere Node.js 20 o posterior; no necesita instalar paquetes.

```powershell
cd frontend
npm start
```

Abrir http://127.0.0.1:4173. `npm test` ejecuta los estados principales. Los escenarios de evaluación se activan en `/?scenario=insufficient` y `/?scenario=error`; envía la pregunta con **Explorar evidencia**. Una petición clínica como «¿Debería cambiar mi medicación?» muestra abstención.

## Qué es real en esta rama

- `fixture.mjs` genera 42 días de registros ficticios y tipados mediante JSDoc, con ausencias explícitas.
- `tools.mjs` ejecuta cobertura, serie temporal y comparación descriptiva sobre esos registros. La interfaz deriva cada cifra de esas respuestas locales.
- `app.mjs` muestra resultado, huecos temporales, trazas locales, procedencia, incertidumbre, abstención y fallo.
- Ningún resultado estadístico, asociación, diagnóstico o prueba causal se simula. El paso de Discovery está marcado como bloqueado.

## Contratos de integración necesarios

La capa visual consume un objeto de investigación. Un adaptador posterior deberá validar el esquema y convertir las respuestas reales sin alterar los contratos del backend:

| Contrato requerido | Campos mínimos |
| --- | --- |
| Estado de ejecución | `run_id`, `question`, `status`, inicio/fin, modo real o local |
| Cobertura | ventana/zonahoraria, días elegibles y observados por variable, unidades, ausencias y frescura |
| Serie | fecha local, valor o `null`, unidad, ID de registro y fuente; ausencia sin interpolación |
| Comparación | definición de periodos, N por periodo, método, resultados numéricos validados e IDs de evidencia |
| Discovery | `EXECUTED_FULL`/`EXECUTED_PARTIAL`/`BLOCKED`/`INSUFFICIENT_DATA`, asociaciones solo si validadas, denominadores, corrección, CI y advertencias cuando existan |
| Hallazgos | ID estable, clase observación/asociación/hipótesis/incertidumbre/abstención, texto fundamentado, IDs de evidencia |
| Trazabilidad | plan, herramienta permitida, estado, duración, ID de traza saneado, error público y referencias a resultados |
| Patrocinadores | evidencia auténtica y saneada de consulta Zetaris, memoria Meterless y modelo Nemotron; estado indisponible si no hubo llamada |

El adaptador debe rechazar cifras sin fuente, estados desconocidos y resultados parciales presentados como completos. Las preguntas de seguimiento deben transportar `run_id` y ventana anterior y ejecutar herramientas nuevas cuando proceda.

## Accesibilidad y límites

Hay flujo de teclado, foco visible, descripción de la gráfica, puntos enfocables, diálogo nativo, etiquetas textuales de estado y diseño adaptable. El fixture sirve para ensayar la experiencia; la aceptación de una demo final exige integraciones y análisis científicos auténticos. Las fuentes tipográficas externas tienen sustitutos del sistema si no están disponibles.
