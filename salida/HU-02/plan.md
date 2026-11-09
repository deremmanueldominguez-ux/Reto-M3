# Plan de implementación · HU-02 Consultar el directorio de empleados

Se extiende el código de HU-01 y HU-03, revisado sin ejecutarlo. Ya cubren el listado y la baja visible (CP-01, CP-02, CP-13, CP-14); falta la búsqueda, el filtro y el mensaje sin resultados. Las preguntas abiertas se resuelven con decisiones marcadas **[a revisar]**.

## Modelo de datos
- Sin tablas, columnas ni migración. Sin índices: la búsqueda se hace en Python y no los usaría.

## Endpoints
Solo cambia `GET /api/empleados`, que acepta dos parámetros opcionales. Sin ellos responde como hoy; `POST`, `PUT` y `/baja` no cambian.
- `busqueda` **[a revisar]**: se recorta; vacío equivale a no enviarlo. Coincide si el texto aparece **en cualquier parte** del nombre o del correo **[a revisar]**: `@empresa.com` devuelve a todos.
- **Se filtra en Python, no en SQL.** `lower()` y `LIKE` de SQLite solo pliegan ASCII: «ANA LÓPEZ» no encontraría «Ana López» y CP-07 fallaría. Función `normalizar_texto`: `unicodedata.normalize("NFC", texto).casefold()`, sobre el texto buscado y sobre cada campo. Además, `%` y `_` se tratan como texto normal.
- La búsqueda distingue acentos: «Lopez» no encuentra «López» **[a revisar]**. Ignorarlos solo cambiaría `normalizar_texto`.
- `departamento` **[a revisar]**: se filtra en SQL por igualdad exacta; vacío equivale a no enviarlo.
  - Valor válido sin empleados: 200 con `[]` (CP-17).
  - Valor fuera de la lista: 422 «Corrige el campo departamento: debe ser uno de: ...» **[a revisar]**, por la regla 3. Se valida con `Annotated[..., AfterValidator, Query()]`, reutilizando `comprobar_departamento`; el manejador de `main.py` ya produce ese texto.
- Con ambos parámetros deben cumplirse los dos **[a revisar]**. Los empleados de baja aparecen también al buscar y filtrar, por la regla 5 **[a revisar]**.
- Orden por `id`, sin paginación **[a revisar]**: cada búsqueda carga los empleados en memoria, aceptable con este volumen y a revisar si crece.

## Componentes de React
- `FiltrosDirectorio` (nuevo): input `buscar-empleados` y `<select>` `filtro-departamento`, controlados por `App`. Primera opción «Todos» con valor vacío; el resto sale de `GET /api/departamentos`. Va **fuera de todo `<form>`**: Enter no debe enviar el alta.
- `App`, cuándo se busca **[a revisar]**:
  - Estados `busqueda` (lo escrito) y `busquedaAplicada`. Un efecto aplica lo escrito tras 300 ms; Enter lo aplica al momento (CP-04). Sin botón de buscar, porque las convenciones no lo definen.
  - Otro efecto sobre `[busquedaAplicada, departamento]` llama a `cargarEmpleados` sin espera y sustituye a la carga inicial. Cambiar el departamento filtra de inmediato.
- `App`, cómo se carga:
  - `cargarEmpleados` lee los filtros vigentes de un `useRef`. Así, tras alta, edición o baja, la recarga respeta el filtro activo, aunque una fila nueva o editada pueda no verse **[a revisar]**; `mensaje-exito` confirma la operación.
  - Un contador en `useRef` descarta respuestas de peticiones anteriores: sin él, una respuesta lenta podría pisar una búsqueda más reciente.
  - Guarda junto con la lista si esa respuesta se pidió con filtros (`resultadoFiltrado`). Se calcula con los filtros de la respuesta y no con lo escrito, para que el mensaje no parpadee mientras se teclea.
- `sin-resultados`: se muestra solo con lista vacía y `resultadoFiltrado`. Texto: «No se encontraron empleados con esos criterios» **[a revisar]**; CP-16 y CP-18 solo exigen que no esté vacío.
- Directorio vacío sin filtros: tabla vacía y sin mensaje, como hoy **[a revisar]**.
- `TablaEmpleados` no cambia: sigue visible con cero filas, como en HU-01, y el correo sigue siendo columna visible **[a revisar]**. Los formularios no cambian.

## data-testid
- Nuevos en pantalla, ya definidos en las convenciones: `buscar-empleados`, `filtro-departamento`, `sin-resultados`.
- Sin cambios: `tabla-empleados`, `fila-empleado-{id}`, `numero-empleado-{id}`, `estado-empleado-{id}`.

## Archivos a crear o modificar
- Modificar `app/backend/rutas/empleados.py`: parámetros de `listar_empleados`, `normalizar_texto` y validación de `departamento`. `esquemas.py` y `main.py` no cambian.
- Modificar `app/frontend/src/api.js`: `listarEmpleados({ busqueda, departamento })` con `URLSearchParams`, omitiendo los vacíos; sin argumentos sigue funcionando.
- Modificar `app/frontend/src/App.jsx` y crear `app/frontend/src/componentes/FiltrosDirectorio.jsx`.
- Sin cambios en `vite.config.js` ni `nginx.conf`: ambos proxies conservan los parámetros de consulta.
- **Riesgo para las pruebas [a revisar]:** los casos parten de una base vacía y exigen conteos exactos, pero no hay endpoint de reinicio y `empleados.db` persiste. No se propone añadir uno: para ejecutarlos, respaldar y vaciar la base solo si la persona lo autoriza.
