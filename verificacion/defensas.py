"""Sesión 4 · ¿Están activas las defensas? El orquestador lo consulta aquí (no puede leer variables de entorno:
el hook de seguridad se lo impide). Siempre «pasa»; el log dice el estado."""
import os


def verificar(hu: str | None = None) -> tuple[bool, str]:
    activas = os.environ.get("DEFENSAS", "1") != "0"
    return True, "DEFENSAS ACTIVADAS" if activas else "DEFENSAS DESACTIVADAS (solo en clase)"