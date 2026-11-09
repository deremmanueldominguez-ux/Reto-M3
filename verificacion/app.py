"""Sesión 2 · ¿La app que escribió el desarrollador funciona? Lo decide el código, no el agente.

- Backend: arranca en el puerto 8010 y `GET /api/salud` debe responder.
- Frontend: `npm run build` debe terminar sin errores.
"""
import subprocess
import sys

from verificacion.comun import APP, correr, responde


def verificar_backend() -> tuple[bool, str]:
    if not (APP / "backend" / "main.py").exists():
        return False, "No existe app/backend/main.py"
    proceso = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8010"],
                               cwd=APP / "backend", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        ok, log = responde("http://127.0.0.1:8010/api/salud", intentos=20)
    finally:
        proceso.terminate()
        salida = proceso.communicate(timeout=10)[0]
    return ok, log if ok else f"{log}\n{salida[-3000:]}"


def verificar_frontend() -> tuple[bool, str]:
    carpeta = APP / "frontend"
    if not (carpeta / "package.json").exists():
        return False, "No existe app/frontend/package.json"
    if not (carpeta / "node_modules").exists():
        ok, log = correr(["npm", "install"], carpeta)
        if not ok:
            return False, log
    return correr(["npm", "run", "build"], carpeta)


def verificar(hu: str | None = None) -> tuple[bool, str]:
    ok_b, log_b = verificar_backend()
    ok_f, log_f = verificar_frontend()
    return ok_b and ok_f, f"## Backend\n{log_b}\n\n## Frontend\n{log_f}"