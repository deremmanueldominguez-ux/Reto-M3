# Reporte de la fábrica · HU-05 Consultar antigüedad

**Estado:** LISTA

**Ciclos de corrección:** 0

## Bitácora

- Paso 0 · `verificacion defensas` → DEFENSAS ACTIVADAS. `filtro-seguridad` → `{"sospechosa": false, "motivo": "solo contiene requisitos del producto"}`; veredicto válido.
- Paso 1 · `analista` escribió 3 escenarios (camino feliz) en `criterios.feature`.
- Paso 2 · Compuerta de criterios → válido.
- Paso 3 · 6 preguntas abiertas (meses incompletos, bajas, dónde se consulta, 404, orden por aniversario, reglas de error). La persona decidió continuar.
- Paso 4 · `disenador-pruebas` escribió 6 casos (3 api, 3 e2e) → válido.
- Paso 5 · `arquitecto` escribió el plan. La persona aprobó con un comentario: `docker-compose.yml` debe definir `FECHA_HOY=2026-11-08` (rechazos: 1 de 2). El plan se rehízo y la persona lo aprobó; el cambio de compose se asignó al agente de despliegue (es su rol).
- Paso 6 · `desarrollador` creó `antiguedad.py` y `TablaEmpleados.jsx`; modificó `esquemas.py`, `api.js`, `App.jsx`, `FormularioEmpleado.jsx`. No pudo ejecutar Python (su rol solo permite `.venv/bin/python`).
- Paso 7 · `verificacion app` → OK.
- Paso 8 · En paralelo: `despliegue` añadió `FECHA_HOY=2026-11-08` al backend y levantó los contenedores; `automatizador` escribió `test_hu_05.py` (3 api) y `test_hu_05_e2e.py` (3 e2e), localizando empleados por correo.
- Paso 9 · `verificacion despliegue` → OK; `verificacion pruebas HU-05` → OK (25 tests recogidos).
- Paso 10 · `verificacion e2e HU-05` → OK: 25 passed, 1 warning.
- Paso 11 · No hizo falta triage.

## Pendientes para una persona

- Añadir el data-testid `antiguedad-empleado-{id}` a `contexto/convenciones_app.md` (ningún agente puede escribir en `contexto/`).
- En `hooks/roles.py`, el rol `desarrollador` permite `.venv/bin/python`, que no existe en Windows; cambiarlo a mano a `.venv/Scripts/python` (hooks/ está protegido por la regla 5).
- Revisar las decisiones [a revisar] del plan: meses completos, plural fijo («1 años 1 meses»), antigüedad de bajas hasta `fecha_baja`, sin 404 ni orden por aniversario.
- `FECHA_HOY=2026-11-08` queda fijo en `docker-compose.yml`: en producción la app no avanzará de fecha hasta quitarlo.

## salida/HU-05/fallos.md

```
# Pruebas de HU-05

25 passed, 1 warning in 18.03s
```
