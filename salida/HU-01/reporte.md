# Reporte HU-01 · Registrar empleado

**Estado:** LISTA
**Ciclos de corrección:** 0

## Bitácora
- Paso 0 · Filtro de seguridad: defensas ACTIVADAS; filtro-seguridad → `sospechosa: false` («solo contiene requisitos del producto»); veredicto.json válido.
- Paso 1 · Analista: 10 escenarios en criterios.feature.
- Paso 2 · Compuerta: criterios.feature válido.
- Paso 3 · Preguntas abiertas: 7 preguntas (texto del mensaje de confirmación, código HTTP 201/200, texto por campo inválido, fecha de hoy, recorte de espacios, varios errores a la vez, consecutivo con bajas). Aprobado por adelantado. Nota: `.venv/bin/python` no existe en Windows; se usó `.venv/Scripts/python`.
- Paso 4 · Diseñador: 19 casos (10 api, 9 e2e); casos_prueba.json válido.
- Paso 5 · Plan: arquitecto escribió plan.md (FastAPI + SQLAlchemy/SQLite, React + Vite). Aprobado por adelantado.
- Paso 6 · Desarrollador: backend y frontend implementados según el plan.
- Paso 7 · Verificación app: OK al primer intento (salud 200, build de Vite correcto).
- Paso 8 · Despliegue y automatizador en paralelo: contenedores levantados (8000 y 8080); 19 pruebas escritas en app/tests/.
- Paso 9 · Unión: verificación despliegue OK; verificación pruebas HU-01 OK (19 recolectadas).
- Paso 10 · E2E: 19 passed, 1 warning → LISTA.
- Paso 11 · Triage: no fue necesario.

## Observaciones
- El hook de rol (`hooks/roles.py`) solo permite `.venv/bin/python`, que no existe en Windows; el desarrollador y el automatizador no pudieron autoverificarse. Conviene permitir `.venv/Scripts/python`.
- Las 7 preguntas abiertas siguen sin respuesta; el plan adoptó supuestos (201, «Empleado registrado con número EMP-XXXX», recorte de espacios, informar solo el primer error).

## fallos.md
```
# Pruebas de HU-01

19 passed, 1 warning in 7.02s
```
