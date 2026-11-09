# Bitácora · interacciones con Claude Code en reto_M3

Sesión del 2026-11-08. Una entrada por petición: qué pedí, qué se hizo y qué quedó pendiente.

## 1. Lab 4D · una regla nueva en `hooks/seguridad.py`

- **Pedí:** una regla nueva, probada sin modelo, con su línea en `auditoria.jsonl`, documentada en docstrings, README y CHANGELOG.
- **Claude:** propuso un plan (bloquear `curl`/`wget` fuera de localhost) y esperó aprobación, como pide `CLAUDE.md`. No se aplicó: cambié la petición.

## 2. Regla 5 · autoprotección de las defensas

- **Pedí:** que una historia envenenada no pueda hacer que el agente modifique el propio hook, `settings.json` ni vacíe la auditoría.
- **Se hizo** (`hooks/seguridad.py`):
  - Write/Edit/MultiEdit/NotebookEdit bloqueados sobre `hooks/`, `.claude/settings*.json` y `auditoria.jsonl`.
  - Bash/PowerShell bloqueados si nombran esos archivos y los modifican (`>`, `rm`, `sed -i`, `Clear-Content`...); leerlos sigue permitido.
  - Cada línea de `auditoria.jsonl` lleva `decision` y, si se bloqueó, `motivo`. `bloquear()` lanza `Bloqueo`.
  - El señuelo pasó a `"BANDERA" + "-DEMO"`: la regla 3 bloqueaba editar el propio archivo.
- **Probé** en mi terminal: `echo '{"tool_name":"Bash","tool_input":{"command":"rm auditoria.jsonl"}}' | .venv/Scripts/python hooks/seguridad.py` → código 2.
- **Documentado** en README (tabla de defensas, «Probar los hooks sin modelo») y en un `CHANGELOG.md` nuevo.

## 3. `/fabrica` · HU-05 Consultar antigüedad

- **Primer intento:** pasé `historias/HU-05 · Consultar antigüedad`; el archivo no existía. Claude se detuvo sin leer `backlog.md` (el orquestador nunca lee historias). Creé `historias/HU-05-consultar-antigüedad.md`.
- **Paso 0:** filtro de seguridad → no sospechosa.
- **Pasos 1–3:** 3 escenarios; compuerta OK; 6 preguntas abiertas. Decidí continuar.
- **Paso 4:** 6 casos (3 API, 3 e2e), válidos.
- **Paso 5:** aprobé el plan con un comentario: `docker-compose.yml` define `FECHA_HOY=2026-11-08` (1 rechazo de 2). Ese cambio se asignó al agente de despliegue (su rol).
- **Pasos 6–9:** desarrollador implementó; `verificacion app`, `despliegue` y `pruebas` OK. El automatizador localiza empleados por correo, no por EMP-xxxx.
- **Paso 10:** e2e 25 passed → **LISTA**, 0 ciclos. Reporte en `salida/HU-05/reporte.md`.

## 4. Revisión de pendientes de HU-05

- `antiguedad-empleado-{id}` ya está en `contexto/convenciones_app.md`.
- `hooks/roles.py` ya permite `.venv/Scripts/python` al desarrollador.
- `.claude/agents/desarrollador.md` ya usa `.venv/Scripts/python` (sin `.exe`), en línea con el hook.
- Siguen abiertos: las decisiones «[a revisar]» del plan (meses completos, «1 años 1 meses», bajas, sin 404) y `FECHA_HOY` fijo en el compose.

## 5. Sandbox para las pruebas del automatizador

- **Pedí:** integrar `ejecutar_en_sandbox` de `hooks/seguridad.py` en los tests del automatizador.
- **Claude encontró:** `registrar()` no existía (NameError); la función aceptaba un solo módulo, no el árbol `app/tests/`; sin autocarga de plugins faltaba Playwright; 20 s era poco para la e2e.
- **Yo (a mano, `hooks/` está protegido):** pegué `ejecutar_pruebas_en_sandbox()` y el atajo `ejecutar_en_sandbox()`. Una línea se cortó al pegar y dejó el hook con SyntaxError (las defensas no bloqueaban nada); la corregí.
- **Claude:** `verificacion/e2e.py` y `verificacion/pruebas.py` corren en el sandbox; docstrings, README y CHANGELOG.
- **Resultado:** `pruebas HU-05` 25 recogidos; `e2e HU-05` 25 passed. Sandbox: pasa / falla / corta a los 20 s, cada corrida con su línea `"herramienta": "sandbox"` en `auditoria.jsonl`.
- **Límite:** aísla intérprete, entorno, carpeta y tiempo; no bloquea red ni disco.

## Pendientes

- Revisar las decisiones «[a revisar]» del plan de HU-05.
- Quitar o acotar `FECHA_HOY=2026-11-08` del compose fuera de las pruebas.
