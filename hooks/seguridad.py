"""Hook PreToolUse · Sesión 4 · Defensas para TODOS los agentes (también el principal).

La historia de usuario es contenido NO confiable: puede traer instrucciones escondidas para el agente
(inyección de prompt, ver historias/HU-99-envenenada.md). Estas defensas no dependen de que el modelo
«se dé cuenta»: son código que se ejecuta antes de cada herramienta.

1. Lectura confinada: nada fuera del proyecto y ningún archivo con secretos.
2. Terminal: sin sustitución de comandos y sin mencionar secretos ni variables de entorno.
3. Escritura: ningún archivo puede contener el señuelo de secretos_demo.txt (prevención de fuga).
4. Auditoría: cada herramienta queda registrada en auditoria.jsonl, con su decisión
   ("permitida" o "bloqueada") y, si se bloqueó, el motivo.
5. Autoprotección: ningún agente puede modificar las propias defensas. Una historia envenenada que pida
   «edita hooks/seguridad.py», «quita el hook de settings.json» o «vacía auditoria.jsonl» se bloquea:
   - Write/Edit/MultiEdit/NotebookEdit sobre hooks/, .claude/settings*.json o auditoria.jsonl.
   - Bash/PowerShell que nombre uno de esos archivos y además lo modifique (redirección `>`, rm, mv,
     cp, truncate, tee, sed -i, Set-Content, Clear-Content, ...). Leerlos (cat, tail, grep) sí se permite.
   Para cambiar las defensas, una persona edita los archivos a mano (o en clase con DEFENSAS=0).

DEFENSAS=0 las apaga, SOLO en clase, para ver el ataque funcionar (hooks/rol.py también relaja la lectura).

Prueba sin modelo (código 2 = bloqueado; mira la última línea de auditoria.jsonl):
    echo '{"tool_name":"Bash","tool_input":{"command":"rm auditoria.jsonl"}}' | .venv/Scripts/python hooks/seguridad.py
"""
import json
import os
import re
import sys
import time
from pathlib import Path
import subprocess
import tempfile
import shutil   # junto a los demás imports; quita ast y datetime


TIEMPO_SANDBOX = 20          # segundos para correr las pruebas

RAIZ = Path(__file__).resolve().parent.parent
SECRETOS = (".env", "secretos")
# \b = borde de palabra: bloquea `env` o `printenv`, pero no `uv venv` ni `.venv/bin/python`
PALABRAS_SECRETAS = re.compile(r"\.env\b|secretos|\bprintenv\b|\benviron\b|\benv\b")
# Partido en dos para que este mismo archivo no contenga el señuelo (la regla 3 impediría editarlo)
SENUELO = "BANDERA" + "-DEMO"

# Regla 5 · Autoprotección: los archivos que sostienen las defensas
PROTEGIDOS_DIRS = (RAIZ / "hooks",)
PROTEGIDOS_ARCHIVOS = (RAIZ / ".claude" / "settings.json", RAIZ / ".claude" / "settings.local.json",
                       RAIZ / "auditoria.jsonl")
# Cómo se nombran en un comando de terminal (con / o con \)
MENCIONA_PROTEGIDO = re.compile(r"hooks[/\\]|settings(\.local)?\.json|auditoria\.jsonl", re.IGNORECASE)
# Operaciones que modifican un archivo: redirección, programas que escriben/borran y cmdlets de PowerShell
MODIFICA = re.compile(
    r">|\b(rm|rmdir|mv|cp|truncate|tee|dd|ln|chmod|shred|unlink|install)\b|\bsed\b.*\s-i"
    r"|\b(remove-item|set-content|clear-content|add-content|out-file|move-item|copy-item|new-item|del|erase)\b",
    re.IGNORECASE)
TRAMOS = re.compile(r"&&|\|\||[;|\n]")


class Bloqueo(Exception):
    """Una regla rechazó la herramienta; el motivo va al agente (stderr) y a auditoria.jsonl."""






def bloquear(motivo: str) -> None:
    raise Bloqueo(motivo)


def auditar(datos: dict, decision: str = "permitida", motivo: str | None = None) -> None:
    """Agrega una línea a auditoria.jsonl: quién, qué herramienta, con qué entrada y qué se decidió."""
    registro = {"ts": round(time.time(), 1), "agente": datos.get("agent_type") or "principal",
                "herramienta": datos["tool_name"], "entrada": str(datos.get("tool_input", {}))[:300],
                "decision": decision}
    if motivo:
        registro["motivo"] = motivo
    with open(RAIZ / "auditoria.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

def ejecutar_pruebas_en_sandbox(origen: Path, argumentos: list[str], variables: dict | None = None,
                                tiempo: int = TIEMPO_SANDBOX) -> dict:
    """Copia `origen` a una carpeta temporal y corre pytest ahí: intérprete aislado (-I), entorno mínimo,
    solo los plugins que pedimos y tiempo límite. No bloquea la red (las pruebas usan localhost)."""
    with tempfile.TemporaryDirectory(prefix="fabrica_") as carpeta:
        destino = Path(carpeta, "tests")
        shutil.copytree(origen, destino, ignore=shutil.ignore_patterns("__pycache__"))
        entorno = {"PATH": os.pathsep.join([str(Path(sys.executable).parent), "/usr/bin", "/bin"]),
                   "PYTHONDONTWRITEBYTECODE": "1", "HOME": carpeta, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                   **(variables or {})}
        if os.name == "nt":
            entorno["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", r"C:\Windows")
            entorno["PLAYWRIGHT_BROWSERS_PATH"] = str(Path(os.environ.get("LOCALAPPDATA", carpeta), "ms-playwright"))
        comando = [sys.executable, "-I", "-X", "utf8", "-m", "pytest", "-p", "no:cacheprovider",
                   "-p", "pytest_playwright.pytest_playwright", *argumentos, str(destino)]
        try:
            proc = subprocess.run(comando, cwd=carpeta, env=entorno, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=tiempo)
            resultado = {"ok": proc.returncode == 0, "salida": (proc.stdout + proc.stderr)[-3000:]}
        except subprocess.TimeoutExpired:
            resultado = {"ok": False, "salida": f"las pruebas pasaron de {tiempo} s y se detuvieron"}
    auditar({"tool_name": "sandbox", "agent_type": "verificacion", "tool_input": {"origen": str(origen)}},
            "permitida" if resultado["ok"] else "bloqueada",
            None if resultado["ok"] else "las pruebas fallaron en el sandbox")
    return resultado


def ejecutar_en_sandbox(codigo: str, pruebas: str) -> dict:
    """Atajo para un módulo y su archivo de pruebas (la interfaz original)."""
    with tempfile.TemporaryDirectory(prefix="fabrica_src_") as fuente:
        Path(fuente, "modulo.py").write_text(codigo, encoding="utf-8")
        Path(fuente, "test_modulo.py").write_text(pruebas, encoding="utf-8")
        return ejecutar_pruebas_en_sandbox(Path(fuente), ["-q"])

def es_protegido(ruta: str) -> bool:
    """¿La ruta (relativa al proyecto o absoluta) cae en un archivo o carpeta de las defensas?"""
    destino = (RAIZ / ruta).resolve()
    return destino in PROTEGIDOS_ARCHIVOS or any(destino.is_relative_to(d) for d in PROTEGIDOS_DIRS)


def comando_modifica_protegido(comando: str) -> bool:
    """Regla 5 en la terminal: algún tramo del comando nombra un archivo protegido y además lo modifica."""
    return any(MENCIONA_PROTEGIDO.search(t) and MODIFICA.search(t) for t in TRAMOS.split(comando))


def revisar(herramienta: str, entrada: dict) -> None:
    """Aplica las reglas 1, 2, 3 y 5; si una falla, lanza Bloqueo con el motivo."""
    if herramienta in ("Read", "Glob", "Grep"):
        ruta = entrada.get("file_path") or entrada.get("path") or "."
        destino = (RAIZ / ruta).resolve()
        if not destino.is_relative_to(RAIZ):
            bloquear(f"lectura fuera del proyecto bloqueada: {ruta}")
        if any(s in destino.name.lower() for s in SECRETOS) and not destino.name.endswith(".example"):
            bloquear(f"archivo con secretos bloqueado: {destino.name}")
    elif herramienta in ("Bash", "PowerShell"):
        comando = entrada.get("command", "")
        if "`" in comando or "$(" in comando:
            bloquear("sustitución de comandos no permitida")
        if PALABRAS_SECRETAS.search(comando.lower()):
            bloquear("el comando menciona secretos o variables de entorno")
        if comando_modifica_protegido(comando):
            bloquear("el comando modifica las defensas (hooks/, settings.json o auditoria.jsonl)")
    elif herramienta in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        ruta = entrada.get("file_path") or entrada.get("notebook_path") or ""
        if ruta and es_protegido(ruta):
            bloquear(f"no se pueden modificar las defensas: {ruta}")
        contenido = (entrada.get("content") or entrada.get("new_string") or entrada.get("new_source")
                     or json.dumps(entrada.get("edits", "")))
        if SENUELO in contenido:
            bloquear("el contenido incluye datos de secretos_demo.txt (fuga de información)")


if __name__ == "__main__":
    datos = json.load(sys.stdin)
    if os.environ.get("DEFENSAS", "1") == "0":
        sys.exit(0)
    try:
        revisar(datos["tool_name"], datos.get("tool_input", {}))
    except Bloqueo as b:
        auditar(datos, "bloqueada", str(b))
        print(f"Seguridad: {b}", file=sys.stderr)
        sys.exit(2)
    auditar(datos)
    sys.exit(0)
