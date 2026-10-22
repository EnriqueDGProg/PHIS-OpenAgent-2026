# PHIS · demo integrada con núcleo Python

La interfaz consume `POST /api/investigations` del núcleo público Python. Los 84 días son **exclusivamente sintéticos** y las cifras se calculan una sola vez en `src/phis_open_agent/tools.py`. Zetaris, Meterless y Nemotron figuran como `NOT_CONNECTED`; esta rama no acredita la integración obligatoria de patrocinadores.

## Ejecutar

Requiere Python 3.11+ y Node.js 20+; no instala paquetes ni crea recursos de pago.

```powershell
cd frontend
npm start
```

El lanzador inicia el servidor Python en `http://127.0.0.1:4173`, que sirve la UI y la API en el mismo origen. Alternativamente, desde la raíz:

```powershell
$env:PYTHONPATH='src'
python -m phis_open_agent.api
```

`GET /api/health` confirma el modo sintético. El endpoint solo acepta `question`, `parent_run_id` opcional y `scenario` de evaluación (`normal`, `insufficient`, `tool_error`). Las URLs `/?scenario=insufficient` y `/?scenario=tool_error` ensayan estados de error explícitamente sintéticos. «¿Debería cambiar mi medicación?» y «Demuestra que dormir poco causó mi cansancio» generan abstención. El chip «¿Y el sueño?» conserva el ID de la ejecución previa, usa la misma ventana y ejecuta herramientas Python nuevas.

## Pruebas

Desde la raíz:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
cd frontend
npm test
```

`tests/test_integration_api.py` levanta el servidor real en un puerto efímero y comprueba que comparación, fuente, huecos, abstención, seguimiento, errores y contenidos servidos coinciden con el núcleo. `frontend/tests/client.test.mjs` protege la frontera de respuesta que entra en la UI.

## Contrato y límites

`contracts/investigation.v1.schema.json` y `.d.ts` fijan ejecución, `dataset_id`, ventana, cobertura, serie con nulos, medias del núcleo, hallazgos, traza y pruebas de patrocinadores. El frontend no importa `fixture.mjs` ni `tools.mjs`; esos módulos se eliminan en esta rama. La API clasifica solo preguntas acotadas de energía/sueño mediante reglas explícitas. No hay LLM, PHIS privado, análisis de asociación o consejo médico. El umbral de 14 observaciones por periodo es una política de presentación descriptiva del adaptador; queda identificado como bloqueo cuando falla.

Las fuentes de Google Fonts son opcionales y el CSS tiene fuentes de sistema de reserva. El panel de evidencias no muestra trazas de sponsor como verificadas sin llamada real.
