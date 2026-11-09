# language: es
Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  para mantener el directorio al día sin perder el historial.

  Escenario: Cambio exitoso de puesto y departamento
    Dado que existe un empleado con número de empleado "EMP-0001", correo "ana.lopez@empresa.com", puesto "Analista de datos", departamento "Tecnología" y estado "activo"
    Cuando edito al empleado "EMP-0001" con puesto "Contadora" y departamento "Finanzas"
    Entonces el directorio muestra al empleado "EMP-0001" con puesto "Contadora" y departamento "Finanzas"
    Y el empleado "EMP-0001" conserva el correo "ana.lopez@empresa.com"
    Y el empleado "EMP-0001" conserva el estado "activo"
    Y el empleado "EMP-0001" no tiene fecha de baja

  Escenario: Baja exitosa de un empleado que sigue en el directorio
    Dado que existe un empleado con número de empleado "EMP-0001", fecha de ingreso "2024-03-01" y estado "activo"
    Cuando doy de baja al empleado "EMP-0001" con fecha de baja "2024-09-30"
    Entonces el empleado "EMP-0001" queda con estado "baja" y fecha de baja "2024-09-30"
    Y el directorio muestra 1 empleado
    Y el directorio muestra al empleado "EMP-0001" marcado como "Baja"

  Escenario: Baja con fecha igual a la fecha de ingreso
    Dado que existe un empleado con número de empleado "EMP-0001", fecha de ingreso "2024-03-01" y estado "activo"
    Cuando doy de baja al empleado "EMP-0001" con fecha de baja "2024-03-01"
    Entonces el empleado "EMP-0001" queda con estado "baja" y fecha de baja "2024-03-01"

  Escenario: El formulario de edición no permite cambiar número de empleado ni correo
    Dado que existe un empleado con número de empleado "EMP-0001", correo "ana.lopez@empresa.com" y estado "activo"
    Cuando abro el formulario de edición del empleado "EMP-0001"
    Entonces el formulario no permite escribir en el campo "numero_empleado"
    Y el formulario no permite escribir en el campo "correo"

  Escenario: La API no cambia el número de empleado ni el correo
    Dado que existe un empleado con número de empleado "EMP-0001", correo "ana.lopez@empresa.com" y estado "activo"
    Cuando envío a la API una edición del empleado "EMP-0001" con número de empleado "EMP-0099" y correo "ana.nueva@empresa.com"
    Entonces el empleado "EMP-0001" conserva el correo "ana.lopez@empresa.com"
    Y no existe un empleado con número de empleado "EMP-0099"

  Escenario: Error por puesto demasiado corto
    Dado que existe un empleado con número de empleado "EMP-0001", puesto "Analista de datos", departamento "Tecnología" y estado "activo"
    Cuando edito al empleado "EMP-0001" con puesto "A" y departamento "Tecnología"
    Entonces la API responde con código 422
    Y la pantalla indica que se debe corregir el campo "puesto"
    Y el empleado "EMP-0001" conserva el puesto "Analista de datos"

  Escenario: Error por puesto vacío
    Dado que existe un empleado con número de empleado "EMP-0001", puesto "Analista de datos", departamento "Tecnología" y estado "activo"
    Cuando edito al empleado "EMP-0001" con puesto "" y departamento "Tecnología"
    Entonces la API responde con código 422
    Y la pantalla indica que se debe corregir el campo "puesto"
    Y el empleado "EMP-0001" conserva el puesto "Analista de datos"

  Escenario: Error por puesto de más de 60 caracteres
    Dado que existe un empleado con número de empleado "EMP-0001", puesto "Analista de datos", departamento "Tecnología" y estado "activo"
    Cuando edito al empleado "EMP-0001" con un puesto de 61 caracteres y departamento "Tecnología"
    Entonces la API responde con código 422
    Y la pantalla indica que se debe corregir el campo "puesto"
    Y el empleado "EMP-0001" conserva el puesto "Analista de datos"

  Escenario: Error por departamento fuera de la lista permitida
    Dado que existe un empleado con número de empleado "EMP-0001", puesto "Analista de datos", departamento "Tecnología" y estado "activo"
    Cuando edito al empleado "EMP-0001" con puesto "Analista de datos" y departamento "Marketing"
    Entonces la API responde con código 422
    Y la pantalla indica que se debe corregir el campo "departamento"
    Y el empleado "EMP-0001" conserva el departamento "Tecnología"

  Escenario: Error por fecha de baja anterior a la fecha de ingreso
    Dado que existe un empleado con número de empleado "EMP-0001", fecha de ingreso "2024-03-01" y estado "activo"
    Cuando doy de baja al empleado "EMP-0001" con fecha de baja "2024-02-29"
    Entonces la API responde con código 422
    Y la pantalla indica que se debe corregir el campo "fecha_baja"
    Y el empleado "EMP-0001" conserva el estado "activo"
    Y el empleado "EMP-0001" no tiene fecha de baja

  Escenario: Error al editar a un empleado dado de baja
    Dado que existe un empleado con número de empleado "EMP-0001", puesto "Analista de datos", departamento "Tecnología", fecha de ingreso "2024-03-01" y estado "activo"
    Y que el empleado "EMP-0001" fue dado de baja con fecha de baja "2024-09-30"
    Cuando edito al empleado "EMP-0001" con puesto "Contadora" y departamento "Finanzas"
    Entonces la API responde con código 409
    Y la pantalla muestra el mensaje "No se puede editar a un empleado dado de baja"
    Y el empleado "EMP-0001" conserva el puesto "Analista de datos"
    Y el empleado "EMP-0001" conserva el departamento "Tecnología"

# Preguntas abiertas
# - ¿Cuáles son las rutas y métodos de la API para editar y para dar de baja, y qué código devuelven al tener éxito?
# - ¿La API rechaza con un error una edición que incluye número de empleado o correo, o ignora esos campos? ¿Con qué código y mensaje?
# - ¿Se pueden editar el nombre y la fecha de ingreso? La historia solo menciona puesto y departamento, y las reglas no lo prohíben.
# - ¿La persona de Recursos Humanos escribe la fecha de baja o la asigna el sistema con la fecha del día?
# - ¿Qué responde el sistema si se da de baja sin indicar la fecha de baja?
# - ¿Se acepta una fecha de baja futura?
# - ¿Qué responde el sistema al dar de baja a un empleado que ya está dado de baja? ¿Aplica el 409 de la regla 6 o se conserva otra respuesta?
# - ¿Se puede reactivar a un empleado dado de baja o corregir su fecha de baja?
# - ¿Qué responde el sistema al editar o dar de baja a un empleado que no existe?
# - ¿«Sin perder el historial» significa solo conservar el registro del empleado, o también guardar los puestos y departamentos anteriores?
# - ¿Se pide confirmación en pantalla antes de dar de baja?
# - ¿Qué texto muestra la pantalla al guardar una edición o una baja con éxito?
# - ¿El directorio debe mostrar la fecha de baja o solo la marca «Baja»?
