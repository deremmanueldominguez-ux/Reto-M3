"""MCP · servidor: publica las herramientas del directorio de empleados para CUALQUIER agente.

Lo que distingue a MCP en el código: la herramienta ya no vive dentro del agente. Aquí solo hay
funciones con anotaciones de tipo y un docstring; FastMCP genera el esquema a partir de ellos y
las sirve por stdio. Quien se conecta (Claude Code, mcp_cliente.py u otro agente) las DESCUBRE
con list_tools() y las usa con call_tool(); no importa este archivo ni sabe cómo están hechas.

Compáralo con react.py: es la misma buscar_empleados, pero allí el esquema JSON se escribía a mano
y solo ese agente podía usarla.

Uso con Claude Code: ya está registrado en .mcp.json (raíz de la sesión). Al abrir `claude`,
acepta el servidor «directorio» y pregunta «¿quién es el empleado activo más antiguo de Tecnología?».
    claude mcp list            # debe decir: directorio … ✔ Connected
Uso sin interacción, viendo el bucle:
    python -m ejemplos.s3_topologias.mcp_cliente
Este archivo no se ejecuta solo: lo arranca el cliente y le habla por la entrada y salida estándar.
Por eso nunca usa print(): cualquier texto en stdout rompería el protocolo.

En tu fábrica: cualquier subagente con la herramienta mcp__directorio__* puede consultar datos de la
empresa sin que cambies su código: se conecta con una línea en .mcp.json.
"""
import json

from mcp.server.fastmcp import FastMCP

from ejemplos.comun import EMPLEADOS

servidor = FastMCP("directorio-empleados", log_level="WARNING")   # sin ruido en la terminal


@servidor.tool()
def buscar_empleados(departamento: str) -> str:
    """Devuelve los empleados de un departamento con su estado y fecha de ingreso.
    Ejemplo: departamento='Tecnología'."""
    encontrados = [e for e in EMPLEADOS if e["departamento"] == departamento]
    return json.dumps(encontrados, ensure_ascii=False) if encontrados else "Sin empleados en ese departamento"


@servidor.tool()
def consultar_empleado(numero: str) -> str:
    """Devuelve los datos de un empleado por su número. Ejemplo: numero='EMP-0003'.
    Si no existe, responde con un error que el agente puede leer."""
    for e in EMPLEADOS:
        if e["numero"] == numero:
            return json.dumps(e, ensure_ascii=False)
    raise ValueError(f"No existe el empleado {numero}")   # MCP lo devuelve como error, no se silencia


# Solo lectura a propósito: un servidor MCP es código de terceros dentro del contexto del agente
# (riesgo de cadena de suministro, ASI04). Publica lo mínimo y sin permisos de escritura.

if __name__ == "__main__":
    servidor.run()   # transporte stdio por defecto