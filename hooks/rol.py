"""Hook PreToolUse · Mínima agencia: cada subagente solo lee, escribe y ejecuta lo de su rol.

Claude Code llama a este script antes de CADA herramienta y le pasa por stdin un JSON con
`agent_type` (el nombre del subagente), `tool_name` y `tool_input`.
- Salida 0  → la herramienta se ejecuta.
- Salida 2  → se bloquea, y lo que imprimimos en stderr le llega al agente como motivo.

Es el equivalente de `_dentro_de()` en agentes/base.py de M3: resolver la ruta y rechazar
cualquier cosa fuera de las carpetas permitidas (incluidos los trucos como `historias/../.env`).
"""
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from hooks.roles import ROLES  # noqa: E402

ESCRITURA = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
LECTURA = {"Read", "Glob", "Grep"}


def bloquear(motivo: str) -> None:
    print(motivo, file=sys.stderr)
    sys.exit(2)


def relativa(ruta: str) -> str | None:
    """Ruta relativa a la raíz, ya resuelta; None si apunta fuera del proyecto."""
    destino = (RAIZ / ruta).resolve()            # si `ruta` es absoluta, Path ignora RAIZ
    if not destino.is_relative_to(RAIZ):
        return None
    return destino.relative_to(RAIZ).as_posix()


def permitida(ruta: str, patrones: list[str]) -> bool:
    rel = relativa(ruta)
    return rel is not None and any(fnmatch.fnmatch(rel, p) for p in patrones)


def revisar(agente: str, herramienta: str, entrada: dict) -> None:
    rol = ROLES[agente]
    if os.environ.get("DEFENSAS", "1") == "0" and herramienta not in ESCRITURA:
        return          # sesión 4, solo en clase: sin defensas de lectura ni de terminal, para ver el ataque
    if herramienta in ESCRITURA:
        ruta = entrada.get("file_path") or entrada.get("notebook_path", "")
        if not permitida(ruta, rol.escribe):
            bloquear(f"Rol {agente}: no puedes escribir {ruta}. Permitido: {', '.join(rol.escribe)}")
    elif herramienta in LECTURA:
        ruta = entrada.get("file_path") or entrada.get("path")
        if not ruta:
            bloquear(f"Rol {agente}: indica siempre la carpeta con `path`. Puedes leer: {', '.join(rol.lee)}")
        if not permitida(ruta, rol.lee + rol.escribe) and not permitida(ruta.rstrip("/") + "/x", rol.lee):
            bloquear(f"Rol {agente}: no puedes leer {ruta}. Permitido: {', '.join(rol.lee)}")
    elif herramienta == "Bash":
        for tramo in re.split(r"&&|\|\||;|\|", entrada.get("command", "")):
            partes = tramo.split()
            if partes and partes[0] not in rol.programas:
                permitidos = ", ".join(sorted(rol.programas)) or "ninguno"
                bloquear(f"Rol {agente}: el programa {partes[0]} no está permitido. Permitidos: {permitidos}")
            if partes and partes[0] == "cd" and len(partes) > 1 and relativa(partes[1]) is None:
                bloquear(f"Rol {agente}: no puedes salir del proyecto con cd {partes[1]}")


if __name__ == "__main__":
    datos = json.load(sys.stdin)
    agente = datos.get("agent_type")
    if agente in ROLES:                           # el agente principal y otros no se restringen aquí
        revisar(agente, datos["tool_name"], datos.get("tool_input", {}))
    sys.exit(0)