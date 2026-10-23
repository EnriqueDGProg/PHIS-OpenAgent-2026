# PHIS · release candidate sintética

La UI consume `POST /api/investigations`. Esa ruta ejecuta `SyntheticAgent`, que selecciona herramientas deterministas del núcleo Python según pregunta, cobertura y estado persistido en el Meterless World Model Engine de referencia. Los adaptadores opcionales de inferencia y Zetaris no se llaman desde esta rama. Todos los registros son ficticios.

## Ejecutar

Requiere Python 3.11+ y Node.js 24. No hace falta instalar paquetes para la demo local.

```powershell
$env:PYTHONPATH='src'
python -m phis_open_agent.api
```

Abre `http://127.0.0.1:4173`. También puedes ejecutar `npm start` desde `frontend/`; el lanzador inicia el mismo servidor Python. El estado sintético del Engine se guarda en `.local-state/.world/agent-events.json`, ignorado por Git. Para elegir otro espacio local, define `PHIS_SYNTHETIC_STATE_FILE`; el Engine usará `<directorio>/.world/<nombre sin extensión>.json`. Conserva ese estado entre reinicios para que el seguimiento recupere decisiones anteriores. El navegador guarda solo el ID sintético de la última investigación comparable.

`GET /api/health` solo declara disponibilidad del proceso y no acredita ningún sponsor. Cada POST acredita `meterless_engine` únicamente después de escribir y releer un evento persistido; Meterless Runtime/Power, NVIDIA y Zetaris siguen sin conectar. El POST acepta `question`, `parent_run_id` opcional y `scenario`: `normal`, `insufficient` o `tool_error`. Los dos últimos son controles de evaluación explícitamente sintéticos; se activan en la UI con `/?scenario=insufficient` y `/?scenario=tool_error`.

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

La prueba heredada de PR #6 abre Chrome de escritorio y móvil con un perfil temporal, usa los archivos reales del checkout e invoca el manejador Python para cada POST mediante un puente sin socket. Ese puente sigue usando el almacén JSONL anterior y **no sirve como prueba del Engine**; para ello ejecuta `tests/test_meterless_engine.py` y `scripts/meterless_engine_trace.py`. El transporte se intercepta porque el sandbox de esa ejecución bloqueó conexiones a `127.0.0.1`; **no demuestra una conexión HTTP real desde Chrome**. Las capturas heredadas están en `docs/evidence/rc-*.png`.

## Contrato y límites

Se mantiene `investigation.v1`. `tool_trace` añade campos opcionales `phase`, `reason_code` y `parent_event_id`, sin romper consumidores anteriores. La UI muestra únicamente herramientas que aparecen en la traza persistida; el gráfico usa puntos y huecos devueltos por Python. Las comparaciones son descriptivas. El umbral de 14 días observados por periodo es una regla operativa de completitud, no significancia científica. No hay inferencia causal, consejo médico ni integración de Meterless Runtime/Power, Nemotron o Zetaris en esta rama. La [matriz del Engine](../docs/METERLESS_ENGINE_CONFORMANCE_2026-10-22.md) documenta el cumplimiento local y sus límites.
