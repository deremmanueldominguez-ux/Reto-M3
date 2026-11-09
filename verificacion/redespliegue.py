"""Sesión 4 · Reconstruye los contenedores sin pasar por un agente (después de que el desarrollador corrige)."""
from verificacion.despliegue import redesplegar


def verificar(hu: str | None = None) -> tuple[bool, str]:
    return redesplegar()