# language: es
Característica: Registrar empleado
  Como persona del área de Recursos Humanos,
  quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso,
  para darlo de alta en la empresa.

  Escenario: Registro exitoso de un empleado con número asignado por el sistema
    Dado que no existe ningún empleado con correo "ana.lopez@empresa.com"
    Y el último número de empleado asignado es "EMP-0007"
    Cuando registro un empleado con nombre "Ana López", correo "ana.lopez@empresa.com", puesto "Analista de Datos", departamento "Tecnología" y fecha de ingreso "2024-03-15"
    Entonces el empleado queda guardado con número de empleado "EMP-0008"
    Y el estado del empleado es "activo"
    Y el empleado tiene una fecha y hora de registro asignada por el sistema
    Y la pantalla muestra un mensaje de confirmación que incluye el número "EMP-0008"

  Escenario: El formulario de registro no permite escribir el número de empleado
    Dado que estoy en la pantalla de registro de empleado
    Cuando reviso los campos del formulario
    Entonces el formulario muestra los campos nombre, correo, puesto, departamento y fecha de ingreso
    Y el formulario no muestra ningún campo para escribir el número de empleado

  Escenario: El correo se guarda en minúsculas
    Dado que no existe ningún empleado con correo "carlos.ruiz@empresa.com"
    Cuando registro un empleado con nombre "Carlos Ruiz", correo "Carlos.Ruiz@Empresa.com", puesto "Vendedor", departamento "Ventas" y fecha de ingreso "2024-01-10"
    Entonces el empleado queda guardado con correo "carlos.ruiz@empresa.com"

  Escenario: Correo duplicado sin importar mayúsculas
    Dado que existe un empleado con correo "ana.lopez@empresa.com"
    Cuando registro un empleado con nombre "Ana Lopez", correo "ANA.LOPEZ@empresa.com", puesto "Contadora", departamento "Finanzas" y fecha de ingreso "2024-02-01"
    Entonces la respuesta tiene código 409
    Y se muestra el mensaje "El correo ya está registrado"
    Y no se registra ningún empleado nuevo

  Escenario: Correo que no es corporativo
    Dado que no existe ningún empleado con correo "luis.perez@gmail.com"
    Cuando registro un empleado con nombre "Luis Pérez", correo "luis.perez@gmail.com", puesto "Supervisor", departamento "Operaciones" y fecha de ingreso "2024-05-20"
    Entonces la respuesta tiene código 422
    Y se muestra el mensaje "Usa el correo corporativo @empresa.com"
    Y no se registra ningún empleado nuevo

  Escenario: Fecha de ingreso futura
    Dado que no existe ningún empleado con correo "marta.diaz@empresa.com"
    Cuando registro un empleado con nombre "Marta Díaz", correo "marta.diaz@empresa.com", puesto "Reclutadora", departamento "Recursos Humanos" y fecha de ingreso "2099-01-01"
    Entonces la respuesta tiene código 422
    Y se muestra el mensaje "La fecha de ingreso no puede ser futura"
    Y no se registra ningún empleado nuevo

  Escenario: Nombre demasiado corto
    Dado que no existe ningún empleado con correo "x.gomez@empresa.com"
    Cuando registro un empleado con nombre "X", correo "x.gomez@empresa.com", puesto "Desarrollador", departamento "Tecnología" y fecha de ingreso "2024-04-01"
    Entonces la respuesta tiene código 422
    Y la pantalla indica que se debe corregir el campo "nombre"
    Y no se registra ningún empleado nuevo

  Escenario: Puesto vacío
    Dado que no existe ningún empleado con correo "elena.vega@empresa.com"
    Cuando registro un empleado con nombre "Elena Vega", correo "elena.vega@empresa.com", puesto "", departamento "Finanzas" y fecha de ingreso "2024-04-01"
    Entonces la respuesta tiene código 422
    Y la pantalla indica que se debe corregir el campo "puesto"
    Y no se registra ningún empleado nuevo

  Escenario: Departamento que no está en la lista permitida
    Dado que no existe ningún empleado con correo "jorge.mora@empresa.com"
    Cuando registro un empleado con nombre "Jorge Mora", correo "jorge.mora@empresa.com", puesto "Diseñador", departamento "Marketing" y fecha de ingreso "2024-04-01"
    Entonces la respuesta tiene código 422
    Y la pantalla indica que se debe corregir el campo "departamento"
    Y no se registra ningún empleado nuevo

  Escenario: Fecha de ingreso sin informar
    Dado que no existe ningún empleado con correo "sofia.rios@empresa.com"
    Cuando registro un empleado con nombre "Sofía Ríos", correo "sofia.rios@empresa.com", puesto "Operaria", departamento "Operaciones" y sin fecha de ingreso
    Entonces la respuesta tiene código 422
    Y la pantalla indica que se debe corregir el campo "fecha_ingreso"
    Y no se registra ningún empleado nuevo

# Preguntas abiertas
# - ¿Cuál es el texto exacto del mensaje de confirmación tras guardar (p. ej. «Empleado registrado con número EMP-0008»)?
# - ¿Qué código HTTP responde un registro exitoso (201 o 200) y qué campos devuelve la API?
# - ¿Cuál es el texto exacto que muestra la pantalla para cada campo inválido de la regla 3?
# - ¿Se permite registrar con fecha de ingreso igual al día de hoy? (se asume que sí, pues solo se prohíben fechas futuras)
# - ¿Se recortan los espacios al inicio y al final de nombre, puesto y correo antes de validar longitudes y unicidad?
# - Si llegan varios datos inválidos a la vez, ¿se informan todos los campos o solo el primero? ¿Qué regla prevalece si el correo es duplicado y además otro campo es inválido?
# - ¿El número consecutivo considera también a los empleados dados de baja (no se reutilizan números)?
