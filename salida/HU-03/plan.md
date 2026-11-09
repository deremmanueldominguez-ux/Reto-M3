# Plan de implementación · HU-03 Editar y dar de baja a un empleado

**Punto de partida:** `app/` ya contiene HU-01, HU-02 y una implementación de HU-03. Este plan sustituye al anterior, que aún decía que HU-02 no estaba en `app/`. Se revisó el código contra los 21 casos leyéndolo, sin ejecutarlo: no se halló ninguna brecha, así que **no se propone cambiar código**. Lo que sigue es el diseño que debe conservarse. Las preguntas abiertas se resuelven con decisiones marcadas **[a revisar]**.

## Modelo de datos
- Sin columnas nuevas ni migración: `estado` y `fecha_baja` ya existen en `Empleado`.
- «Sin perder el historial» significa conservar el registro; no se guardan los puestos y departamentos anteriores **[a revisar]**.
- Solo se editan `puesto` y `departamento`. `nombre` y `fecha_ingreso` quedan fijos **[a revisar]**. No hay reactivación ni corrección de la fecha de baja **[a revisar]**.

## Endpoints
- `PUT /api/empleados/{id}` → **200** **[a revisar]** con `EmpleadoRespuesta`. Exige `puesto` (2 a 60 caracteres, tras recortar espacios) y `departamento` (lista permitida).
  - Ignora `numero_empleado`, `correo` y cualquier otro campo, sin error (`extra="ignore"`) **[a revisar]**: cumple CP-09.
  - Empleado inexistente: 404 «Empleado no encontrado» **[a revisar]**. Dado de baja: 409 «No se puede editar a un empleado dado de baja».
- `POST /api/empleados/{id}/baja` → **200** **[a revisar]** con `EmpleadoRespuesta`; cambia `estado` a «baja» y guarda `fecha_baja`, sin borrar el registro.
  - `fecha_baja` es obligatoria y la escribe la persona **[a revisar]**. Ausente, vacía o sin formato ISO: 422.
  - La ruta comprueba en este orden: 404; 409 «El empleado ya está dado de baja» **[a revisar]**, que conserva la fecha original; y 422 «Corrige el campo fecha_baja: no puede ser anterior a la fecha de ingreso». Una fecha igual a la de ingreso se acepta.
  - Una fecha futura se acepta y el estado cambia de inmediato, porque las reglas solo prohíben que sea anterior al ingreso **[a revisar]**. Riesgo: el directorio mostraría «Baja» antes de esa fecha.
- FastAPI valida el cuerpo antes que la ruta: un cuerpo inválido da 422 aunque el empleado no exista o esté de baja **[a revisar]**. Matiz frente a la regla 6, que pide 409 en todo intento; ningún caso combina esas condiciones. Si se quiere 409 siempre, habría que validar dentro de la ruta.
- `main.py` no cambia: los 422 de `puesto` y `departamento` ya dicen «Corrige el campo {campo}: ...», como piden CP-11, CP-13, CP-15 y CP-17.

## Componentes de React
- `App`: estado `accion` (`null`, `{tipo: "editar", empleado}` o `{tipo: "baja", empleado}`) y **un solo formulario a la vez**, porque edición y alta comparten `empleado-puesto` y `empleado-guardar`.
- `App`, mensajes: encima del formulario, para que haya un único `mensaje-error`; se limpian al abrir, cancelar o enviar. Con éxito se cierra el formulario, se recarga la lista respetando los filtros de HU-02 y se muestra `mensaje-exito`. Con error sigue abierto y muestra el `detail`. Textos de éxito **[a revisar]**: «Empleado {numero} actualizado» y «Empleado {numero} dado de baja».
- `FormularioEdicionEmpleado`: `<form noValidate>` con `puesto` y `departamento` precargados, sin `maxLength`, para que CP-15 llegue a la API. `numero_empleado` y `correo` son inputs `disabled`. Envía solo `puesto` y `departamento`. Opciones desde `GET /api/departamentos`, por CP-17.
- `FormularioBaja`: `<form noValidate>` con `type="date"`, sin `min` ni `required`, para que CP-19 reciba el error de la API. Sin paso extra de confirmación **[a revisar]**: el propio formulario la hace.
- `TablaEmpleados`: columna «Acciones». `editar-empleado-{id}` sigue activo con estado «baja», porque CP-21 exige ver el 409 en pantalla. `baja-empleado-{id}` se deshabilita con estado «baja» **[a revisar]**. La fecha de baja no se muestra en el directorio **[a revisar]**.
- Con un filtro de departamento activo, una fila editada puede dejar de verse **[a revisar]**; `mensaje-exito` confirma la operación.

## data-testid
- Acciones y baja: `editar-empleado-{id}`, `baja-empleado-{id}`, `empleado-fecha-baja`, `confirmar-baja`.
- Reutilizados en la edición: `empleado-puesto`, `empleado-departamento`, `empleado-guardar`, y `empleado-correo` en el input `disabled` (CP-08).
- Compartidos: `mensaje-exito`, `mensaje-error`, `tabla-empleados`, `fila-empleado-{id}`, `numero-empleado-{id}`, `estado-empleado-{id}`. El input de `numero_empleado` no lleva `data-testid`: las convenciones no lo definen y CP-08 no lo necesita.

## Archivos a crear o modificar
- **Ninguno por crear ni modificar.** Ya implementan el diseño `app/backend/esquemas.py`, `rutas/empleados.py`, `modelos.py`, `app/frontend/src/api.js`, `App.jsx` y, en `componentes/`, `TablaEmpleados.jsx`, `FormularioEdicionEmpleado.jsx` y `FormularioBaja.jsx`.
- Si la revisión cambia una decisión **[a revisar]**, se modifica solo el archivo afectado: reglas en `esquemas.py` o `rutas/empleados.py`, pantalla en `componentes/`.
- **Pendiente fuera de este plan:** `app/tests/` no tiene pruebas de HU-03 y los casos e2e no se han ejecutado. Los casos exigen una base vacía y `empleados.db` persiste: respaldarla y vaciarla solo si la persona lo autoriza. Los contenedores desplegados pueden no incluir estos cambios.
