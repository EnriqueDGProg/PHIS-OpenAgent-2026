# PHIS · release candidate sintética

La UI de PR #4 consume `POST /api/investigations`. Esa ruta ejecuta `SyntheticAgent` de PR #5, que selecciona herramientas deterministas del núcleo Python según pregunta, cobertura y estado persistido. Los adaptadores opcionales de PR #3 están disponibles en el repositorio, pero esta demo no los llama ni acredita sponsors. Todos los registros son ficticios.

## Ejecutar

Requiere Python 3.11+ y Node.js 20+. No hace falta instalar paquetes para la demo local.

```powershell
$env:PYTHONPATH='src'
python -m phis_open_agent.api
```

Abre `http://127.0.0.1:4173`. También puedes ejecutar `npm start` desde `frontend/`; el lanzador inicia el mismo servidor Python. El estado sintético se guarda en `.local-state/agent-events.jsonl`, ignorado por Git. Para elegir otra ruta local, define `PHIS_SYNTHETIC_STATE_FILE`. Conserva ese archivo entre reinicios para que el seguimiento recupere decisiones anteriores. El navegador guarda solo el ID sintético de la última investigación comparable.

`GET /api/health` declara modo sintético y sponsors desconectados. El POST acepta `question`, `parent_run_id` opcional y `scenario`: `normal`, `insufficient` o `tool_error`. Los dos últimos son controles de evaluación explícitamente sintéticos; se activan en la UI con `/?scenario=insufficient` y `/?scenario=tool_error`.

## Pruebas

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -q
node --test frontend/tests/*.test.mjs
```

`tests/test_integration_api.py` invoca el manejador HTTP en proceso, sin socket, y comprueba que ejecuta el agente, adapta las cifras del núcleo, registra fases reales, se abstiene ante cobertura escasa/fallos y recupera el World Model en una nueva instancia. El cliente Node valida `investigation.v1`, trazas y pruebas de sponsor.

Para capturas reales en Chrome sin instalar dependencias nuevas, si Playwright ya está disponible:

```powershell
$env:PHIS_PLAYWRIGHT_MODULE='RUTA_ABSOLUTA_A_PLAYWRIGHT/index.mjs'
node frontend/tests/e2e_chrome.mjs
```

La prueba abre Chrome de escritorio y móvil con un perfil temporal, usa los archivos reales del checkout e invoca el manejador Python real para cada POST mediante un puente sin socket. Cada petición crea un proceso Python nuevo, por lo que el seguimiento prueba recuperación de estado en disco. El transporte se intercepta porque el sandbox de esta ejecución bloquea conexiones a `127.0.0.1`; **no demuestra una conexión HTTP real desde Chrome**. Las capturas generadas están en `docs/evidence/rc-*.png`.

## Contrato y límites

Se mantiene `investigation.v1`. `tool_trace` añade campos opcionales `phase`, `reason_code` y `parent_event_id`, sin romper consumidores anteriores. La UI muestra únicamente herramientas que aparecen en la traza persistida; el gráfico usa puntos y huecos devueltos por Python. Las comparaciones son descriptivas. El umbral de 14 días observados por periodo es una regla operativa de completitud, no significancia científica. No hay inferencia causal, consejo médico ni integración oficial Meterless/Nemotron/Zetaris.
