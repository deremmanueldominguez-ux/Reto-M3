"""Piezas compartidas por los ejemplos: cómo llamar al modelo SIN API key, unos datos y utilidades.

En M3 los ejemplos llamaban a `Anthropic().messages.create(...)`, que necesita ANTHROPIC_API_KEY.
En M3B llamamos a Claude Code en modo no interactivo (`claude -p`), que usa tu sesión de
`claude auth login`. Es el mismo modelo; cambia quién ejecuta el bucle y las herramientas.

    claude("pregunta")                         → texto
    claude("extrae...", esquema=Modelo)         → dict que cumple el JSON Schema de un modelo Pydantic
    for evento in eventos("pregunta", herramientas="Read,Grep"):  → cada paso del bucle de Claude Code
"""
import json
import os
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Un directorio pequeño, para que los ejemplos no dependan de la app generada
EMPLEADOS = [
    {"numero": "EMP-0001", "nombre": "Ana López", "departamento": "Tecnología", "fecha_ingreso": "2019-03-04", "estado": "activo"},
    {"numero": "EMP-0002", "nombre": "Luis Pérez", "departamento": "Ventas", "fecha_ingreso": "2021-07-19", "estado": "activo"},
    {"numero": "EMP-0003", "nombre": "Marta Ruiz", "departamento": "Tecnología", "fecha_ingreso": "2016-11-02", "estado": "baja"},
    {"numero": "EMP-0004", "nombre": "Jorge Díaz", "departamento": "Tecnología", "fecha_ingreso": "2022-01-10", "estado": "activo"},
    {"numero": "EMP-0005", "nombre": "Sofía Gómez", "departamento": "Finanzas", "fecha_ingreso": "2020-05-25", "estado": "activo"},
]


def _comando(prompt: str, formato: str, herramientas: str, sistema: str | None, esquema: dict | None) -> list[str]:
    cmd = ["claude", "-p", prompt, "--output-format", formato, "--no-session-persistence",
           "--tools", herramientas]                    # "" = sin herramientas: solo razona y responde
    if herramientas:
        cmd += ["--allowedTools", herramientas]        # las herramientas que damos, sin pedir permiso
    if sistema:
        cmd += ["--system-prompt", sistema]
    if esquema:
        cmd += ["--json-schema", json.dumps(esquema)]  # salida estructurada: Claude Code la valida
    return cmd


def _entorno() -> dict:
    """Sin ANTHROPIC_API_KEY a propósito: así Claude Code usa tu suscripción (claude auth login)."""
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def claude(prompt: str, *, esquema: type | None = None, herramientas: str = "",
           sistema: str | None = None) -> str | dict:
    """Una llamada al modelo. Con `esquema` (un modelo Pydantic) devuelve un dict que lo cumple."""
    r = subprocess.run(_comando(prompt, "json", herramientas, sistema,
                                esquema.model_json_schema() if esquema else None),
                       cwd=RAIZ, capture_output=True, text=True, env=_entorno(), stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(f"claude -p falló ({r.returncode}): {(r.stderr or r.stdout)[-500:]}")
    salida = json.loads(r.stdout)
    if salida.get("is_error"):
        raise RuntimeError(f"claude -p devolvió un error: {salida.get('result')}")
    return salida["structured_output"] if esquema else salida["result"]


def eventos(prompt: str, *, herramientas: str, sistema: str | None = None, extra: list[str] = ()):
    """Cada mensaje del bucle de Claude Code, en vivo (stream-json): lo que razona, lo que hace, lo que ve.

    `extra` agrega banderas de `claude`, por ejemplo un servidor MCP (sesión 3).
    """
    cmd = _comando(prompt, "stream-json", herramientas, sistema, None) + ["--verbose", *extra]
    with subprocess.Popen(cmd, cwd=RAIZ, stdout=subprocess.PIPE, text=True, env=_entorno(),
                          stdin=subprocess.DEVNULL) as p:
        for linea in p.stdout:
            if linea.strip():
                yield json.loads(linea)


def historia(nombre: str) -> str:
    """Texto de una historia de usuario de historias/, por ejemplo historia('HU-01')."""
    return next((RAIZ / "historias").glob(f"{nombre}-*.md")).read_text(encoding="utf-8")


def titulo(texto: str) -> None:
    print(f"\n\033[1;33m── {texto} ──\033[0m")


def paso(quien: str, texto: str, limite: int = 300) -> None:
    """Imprime lo que hizo un paso o agente, recortado para que se lea en pantalla."""
    texto = " ".join(str(texto).split())
    print(f"\033[1;36m[{quien}]\033[0m {texto[:limite]}{'…' if len(texto) > limite else ''}")