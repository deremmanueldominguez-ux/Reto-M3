"""Verificaciones deterministas: el código, no un agente, decide si un paso terminó bien.

Cada módulo de esta carpeta define `verificar(hu) -> (ok, log)`. El log regresa al agente
responsable cuando algo falla. Cada sesión agrega un módulo: app (2), despliegue y pruebas (3), e2e (4).
"""
import importlib


def verificar(nombre: str, hu: str | None = None) -> tuple[bool, str]:
    try:
        modulo = importlib.import_module(f"verificacion.{nombre}")
    except ModuleNotFoundError:
        return False, f"No existe la verificación «{nombre}» (verificacion/{nombre}.py)"
    return modulo.verificar(hu)