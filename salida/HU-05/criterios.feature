# language: es
Característica: Consultar antigüedad
  Como persona de Recursos Humanos,
  quiero ver la antigüedad de cada empleado en años y meses,
  para preparar los reconocimientos por aniversario.

  Escenario: Ver la antigüedad en años y meses de cada empleado
    Dado que hoy es "2026-11-08"
    Y que existe el empleado "EMP-0001" "Ana Pérez" con fecha de ingreso "2024-05-08"
    Y que existe el empleado "EMP-0002" "Luis Gómez" con fecha de ingreso "2021-11-08"
    Cuando la persona de Recursos Humanos consulta la antigüedad de los empleados
    Entonces el empleado "EMP-0001" muestra una antigüedad de "2 años 6 meses"
    Y el empleado "EMP-0002" muestra una antigüedad de "5 años 0 meses"

  Escenario: Empleado que ingresó hoy tiene antigüedad cero
    Dado que hoy es "2026-11-08"
    Y que existe el empleado "EMP-0003" "Marta Ruiz" con fecha de ingreso "2026-11-08"
    Cuando la persona de Recursos Humanos consulta la antigüedad de los empleados
    Entonces el empleado "EMP-0003" muestra una antigüedad de "0 años 0 meses"

  Escenario: Antigüedad de un empleado que cumple aniversario este mes
    Dado que hoy es "2026-11-08"
    Y que existe el empleado "EMP-0004" "Carlos Díaz" con fecha de ingreso "2016-11-08"
    Cuando la persona de Recursos Humanos consulta la antigüedad de los empleados
    Entonces el empleado "EMP-0004" muestra una antigüedad de "10 años 0 meses"

# Preguntas abiertas
# - ¿Cómo se cuentan los meses incompletos? (por ejemplo, ingreso "2020-03-15" y hoy "2026-11-08": ¿6 años 7 meses o 6 años 8 meses?)
# - ¿Se muestra la antigüedad de los empleados dados de baja? Si se muestra, ¿se calcula hasta la fecha de baja o hasta hoy?
# - ¿Dónde se consulta la antigüedad: como columna del directorio, en el detalle del empleado o en una pantalla/endpoint propio? ¿Qué ruta de API la expone?
# - ¿Qué responde la API al consultar la antigüedad de un empleado que no existe (por ejemplo, 404 y con qué mensaje)?
# - ¿Se necesita filtrar u ordenar por antigüedad o por mes de aniversario para preparar los reconocimientos?
# - Ninguna de las reglas de negocio 1 a 6 aplica a una consulta de solo lectura, por eso no hay escenarios de error; confirmar si existe alguna regla de error para esta historia.
