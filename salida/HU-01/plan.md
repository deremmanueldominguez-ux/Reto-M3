# Plan HU-01 · Registrar empleado
Plan inicial (sin comentarios previos); `app/` está vacía, se empieza de cero con capas separadas para que las historias futuras (directorio, edición, baja, vacaciones) se agreguen sin reescribir.

## Modelo de datos
- Tabla `empleados` (SQLAlchemy 2, SQLite en `backend/datos/empleados.db`, carpeta creada al arrancar): `id` int PK autoincremental, `numero_empleado` str único, `nombre` str(80), `correo` str único (minúsculas), `puesto` str(60), `departamento` str, `fecha_ingreso` date, `estado` str (default «activo»), `fecha_baja` date nula, `creado_en` datetime (lo asigna el servidor).
- `numero_empleado` = `EMP-` + (máximo consecutivo existente + 1) con 4 dígitos; cuenta también las bajas, nunca se reutiliza.
- Catálogo `DEPARTAMENTOS` como constante: Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones.

## Endpoints (prefijo /api)
- `GET /api/salud` → `{"estado": "ok"}`.
- `GET /api/departamentos` → lista de los 5 departamentos.
- `GET /api/empleados` → lista de empleados (la necesitan los casos para verificar totales).
- `POST /api/empleados` → 201 con el empleado completo. El esquema de entrada solo acepta nombre, correo, puesto, departamento, fecha_ingreso; campos extra (p. ej. `numero_empleado`) se ignoran (CP-03).
- Validación, en este orden: recortar espacios; correo pasa a minúsculas; correo sin `@empresa.com` → 422 «Usa el correo corporativo @empresa.com»; fecha futura → 422 «La fecha de ingreso no puede ser futura» (hoy sí se permite); otros campos inválidos (nombre 2-80, puesto 2-60, departamento fuera del catálogo, fecha ausente o vacía) → 422; correo duplicado → 409 «El correo ya está registrado».
- Manejador de `RequestValidationError` que convierte el error de Pydantic en `{"detail": "Corrige el campo <campo>: <motivo>"}` con el nombre técnico del campo (`nombre`, `puesto`, `departamento`, `fecha_ingreso`), para cumplir la forma de errores y la regla 3.

## Componentes de React
- `App.jsx`: muestra el formulario de registro (punto de montaje para futuras vistas).
- `FormularioEmpleado.jsx`: estado controlado de los 5 campos; carga el selector desde `GET /api/departamentos`; `noValidate` en el `<form>` para que las validaciones las decida el backend; en 201 muestra «Empleado registrado con número EMP-XXXX» y limpia el formulario; en error muestra `detail` tal cual.
- `api.js`: funciones `obtenerDepartamentos()` y `registrarEmpleado(datos)` con rutas relativas `/api/...`.

## data-testid
`empleado-nombre`, `empleado-correo`, `empleado-puesto`, `empleado-departamento` (select), `empleado-fecha-ingreso` (input date), `empleado-guardar`, `mensaje-exito`, `mensaje-error`. Solo uno de los mensajes visible a la vez. No existe ningún campo de número de empleado en el formulario.

## Archivos a crear o modificar
- Backend: `app/backend/main.py` (app, routers, manejador 422, creación de tablas), `database.py` (motor y sesión), `modelos.py`, `esquemas.py` (EmpleadoCrear, EmpleadoSalida), `catalogos.py`, `rutas/empleados.py`, `rutas/departamentos.py`, `requirements.txt` (fastapi, uvicorn, sqlalchemy, pydantic).
- Frontend: `app/frontend/package.json`, `vite.config.js` (puerto 5173, proxy `/api` → 8000), `index.html`, `src/main.jsx`, `src/App.jsx`, `src/api.js`, `src/components/FormularioEmpleado.jsx`.
- Supuestos a confirmar (preguntas abiertas): código 201, texto de confirmación, formato del mensaje por campo, recorte de espacios, informar solo el primer campo inválido.
