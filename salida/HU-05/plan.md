# Plan de implementación · HU-05 Consultar antigüedad

**Comentarios incorporados:** la persona aprobó el plan y pidió un cambio: `app/docker-compose.yml` define `FECHA_HOY=2026-11-08` en el servicio `backend`, para que las pruebas e2e contra la app desplegada sean deterministas. Ese cambio está en «Archivos a crear o modificar». Lo demás no cambia. Hoy `app/` solo tiene HU-01: alta, `GET /api/empleados` sin filtros y ninguna tabla.

## Modelo de datos
- Sin tablas, columnas ni migración. La antigüedad se calcula al responder y no se guarda.
- Nuevo módulo `antiguedad.py` con funciones puras:
  - `calcular_antiguedad(ingreso, hasta) -> (anios, meses)`: `total = (hasta.year - ingreso.year) * 12 + (hasta.month - ingreso.month)`, y se resta 1 si `hasta.day < ingreso.day`. Solo cuentan los meses completos: de 2020-03-15 a 2026-11-08 da «6 años 7 meses». Si el día de ingreso es 29, 30 o 31 y el mes final es más corto, ese mes cuenta como incompleto.
  - `texto_antiguedad(anios, meses)`: siempre «N años M meses», en plural, igual que los criterios.
  - `fecha_hoy()`: lee la variable de entorno opcional `FECHA_HOY` (AAAA-MM-DD). Si no existe, usa `date.today()`.
- Empleado dado de baja: la antigüedad se cuenta hasta su `fecha_baja`, no hasta hoy. Sigue apareciendo, por la regla 5.

## Endpoints
- No hay rutas nuevas: CP-01, CP-03 y CP-05 leen la antigüedad en `GET /api/empleados`.
- `EmpleadoSalida` gana tres `@computed_field` de Pydantic v2: `antiguedad_anios` (int), `antiguedad_meses` (int) y `antiguedad` (str, p. ej. «2 años 6 meses»). Salen en toda respuesta de empleado, también en la del `POST` (201), sin romper los campos actuales.
- `validar_fecha_ingreso` usa `fecha_hoy()` en lugar de `date.today()`, para que la regla 4 y la antigüedad usen el mismo «hoy». Con `FECHA_HOY=2026-11-08`, una alta con fecha de ingreso 2026-11-08 es válida, y una con 2026-11-09 se rechaza.
- Sin errores nuevos: es una consulta de solo lectura. No hay 404 por empleado ni filtros u orden por aniversario.

## Componentes de React
- `TablaEmpleados` (`src/components/`): si HU-02 o HU-03 ya la crearon, solo se le añade la columna «Antigüedad». Si no existe, se crea una mínima con número, nombre, departamento, fecha de ingreso, estado y antigüedad.
- La celda muestra `empleado.antiguedad` tal como llega: el cálculo vive solo en el backend.
- `App.jsx`: llama a `listarEmpleados()` al montar y tras cada alta correcta (`FormularioEmpleado` recibe el callback `alGuardar`). La tabla va debajo del formulario.

## data-testid
- Nuevo: `antiguedad-empleado-{id}` en la celda de antigüedad. Hay que añadirlo a `contexto/convenciones_app.md`.
- Ya existentes, que se usan: `tabla-empleados`, `fila-empleado-{id}`, `numero-empleado-{id}`, `estado-empleado-{id}`. La tabla se ve siempre, aunque tenga cero filas.

## Archivos a crear o modificar
- Crear `app/backend/antiguedad.py`.
- Modificar `app/backend/esquemas.py`: campos calculados en `EmpleadoSalida` y `fecha_hoy()` en `validar_fecha_ingreso`. `rutas/empleados.py` y `modelos.py` no cambian.
- Modificar `app/docker-compose.yml`: añadir `environment: - FECHA_HOY=2026-11-08` al servicio `backend`. Así el «Dado que hoy es 2026-11-08» se cumple en la app desplegada. El frontend no la necesita.
- Modificar `app/frontend/src/api.js`: añadir `listarEmpleados()` (`GET /api/empleados`) si no existe.
- Crear o modificar `app/frontend/src/components/TablaEmpleados.jsx`. Modificar `App.jsx` y `FormularioEmpleado.jsx` (solo el callback `alGuardar`).
- Riesgo para las pruebas: los casos dan por hecho que EMP-0001 a EMP-0004 tienen fechas concretas, pero `numero_empleado` lo asigna el sistema y `empleados.db` persiste en `./backend/datos`. Las pruebas deben buscar a cada empleado por el correo con el que lo dieron de alta, no por el número.
