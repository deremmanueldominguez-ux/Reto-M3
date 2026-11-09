# language: es
Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  para encontrar rápido a una persona.

  Escenario: El directorio muestra los datos de cada empleado
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López", correo "ana.lopez@empresa.com", puesto "Analista de datos", departamento "Tecnología" y estado "activo"
    Cuando abro el directorio de empleados
    Entonces el directorio muestra 1 empleado
    Y la fila muestra número de empleado "EMP-0001", nombre "Ana López", puesto "Analista de datos", departamento "Tecnología" y estado "activo"

  Escenario: Búsqueda de un empleado por nombre
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López" y correo "ana.lopez@empresa.com"
    Y que existe un empleado con número de empleado "EMP-0002", nombre "Luis Pérez" y correo "luis.perez@empresa.com"
    Cuando busco "Ana López" en el directorio
    Entonces el directorio muestra 1 empleado
    Y el directorio muestra al empleado "EMP-0001"
    Y el directorio no muestra al empleado "EMP-0002"

  Escenario: Búsqueda de un empleado por correo
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López" y correo "ana.lopez@empresa.com"
    Y que existe un empleado con número de empleado "EMP-0002", nombre "Luis Pérez" y correo "luis.perez@empresa.com"
    Cuando busco "luis.perez@empresa.com" en el directorio
    Entonces el directorio muestra 1 empleado
    Y el directorio muestra al empleado "EMP-0002"
    Y el directorio no muestra al empleado "EMP-0001"

  Escenario: La búsqueda por nombre no distingue mayúsculas de minúsculas
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López" y correo "ana.lopez@empresa.com"
    Y que existe un empleado con número de empleado "EMP-0002", nombre "Luis Pérez" y correo "luis.perez@empresa.com"
    Cuando busco "ANA LÓPEZ" en el directorio
    Entonces el directorio muestra 1 empleado
    Y el directorio muestra al empleado "EMP-0001"

  Escenario: La búsqueda por correo no distingue mayúsculas de minúsculas
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López" y correo "ana.lopez@empresa.com"
    Y que existe un empleado con número de empleado "EMP-0002", nombre "Luis Pérez" y correo "luis.perez@empresa.com"
    Cuando busco "LUIS.PEREZ@EMPRESA.COM" en el directorio
    Entonces el directorio muestra 1 empleado
    Y el directorio muestra al empleado "EMP-0002"

  Escenario: Filtrar el directorio por departamento
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López" y departamento "Tecnología"
    Y que existe un empleado con número de empleado "EMP-0002", nombre "Luis Pérez" y departamento "Ventas"
    Cuando filtro el directorio por departamento "Ventas"
    Entonces el directorio muestra 1 empleado
    Y el directorio muestra al empleado "EMP-0002"
    Y el directorio no muestra al empleado "EMP-0001"

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López", fecha de ingreso "2024-03-01" y estado "activo"
    Y que el empleado "EMP-0001" fue dado de baja con fecha de baja "2024-09-30"
    Cuando abro el directorio de empleados
    Entonces el directorio muestra 1 empleado
    Y el directorio muestra al empleado "EMP-0001" con estado "baja"

  Escenario: Mensaje cuando la búsqueda no tiene resultados
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López" y correo "ana.lopez@empresa.com"
    Cuando busco "Zacarías Ortega" en el directorio
    Entonces el directorio muestra 0 empleados
    Y la pantalla muestra un mensaje que indica que no hay resultados

  Escenario: Mensaje cuando el filtro por departamento no tiene resultados
    Dado que existe un empleado con número de empleado "EMP-0001", nombre "Ana López" y departamento "Tecnología"
    Cuando filtro el directorio por departamento "Finanzas"
    Entonces el directorio muestra 0 empleados
    Y la pantalla muestra un mensaje que indica que no hay resultados

# Preguntas abiertas
# - ¿Cuál es el texto exacto del mensaje que se muestra cuando no hay resultados?
# - ¿Cuál es la ruta de la API para consultar el directorio y cómo se llaman sus parámetros de búsqueda y filtro?
# - ¿La búsqueda acepta coincidencias parciales (por ejemplo, «ana» o «@empresa.com») o solo el valor completo?
# - ¿La búsqueda distingue acentos (por ejemplo, «Lopez» encuentra a «López»)?
# - ¿Si se combinan búsqueda y filtro por departamento, deben cumplirse ambos a la vez?
# - ¿Qué responde la API si se filtra por un departamento que no está en la lista permitida (422 o lista vacía)?
# - ¿Qué se muestra cuando el directorio está vacío y no se ha buscado ni filtrado: el mismo mensaje u otro?
# - ¿El correo se busca aunque no sea una columna visible del directorio, o también debe mostrarse?
# - ¿Los empleados dados de baja también aparecen al buscar y filtrar, o solo en el listado completo?
# - ¿En qué orden se listan los empleados y hay paginación?
# - ¿La búsqueda se ejecuta al escribir o al confirmar con un botón?
