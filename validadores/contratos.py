"""Sesiones 1 y 4 · Contratos y validadores deterministas.

En M3B los agentes son subagentes de Claude Code, pero la regla del curso no cambia:
el modelo propone y el CÓDIGO decide si el resultado es válido. Estas funciones no usan
ningún modelo: reciben texto y devuelven la lista de problemas (vacía = válido).
"""
import re
from typing import Literal

from pydantic import BaseModel, ValidationError


# --- Criterios de aceptación (agente 1, analista) -------------------------------
def escenarios(gherkin: str) -> list[str]:
    """Nombres de los escenarios, tal como aparecen después de «Escenario:»."""
    return re.findall(r"^\s*Escenario:\s*(.+?)\s*$", gherkin, flags=re.MULTILINE)


def preguntas_abiertas(gherkin: str) -> list[str]:
    """Las líneas de comentario que el analista dejó bajo «# Preguntas abiertas»."""
    if "# Preguntas abiertas" not in gherkin:
        return []
    bloque = gherkin.split("# Preguntas abiertas", 1)[1]
    return [l.lstrip("# -").strip() for l in bloque.splitlines() if l.strip().lstrip("#").strip()]


def validar_gherkin(texto: str) -> list[str]:
    problemas = []
    if not texto.lstrip().startswith("# language: es"):
        problemas.append("La primera línea debe ser '# language: es'.")
    if "Característica:" not in texto:
        problemas.append("Falta 'Característica:'.")
    bloques = re.split(r"^\s*Escenario:", texto, flags=re.MULTILINE)[1:]
    if len(bloques) < 2:
        problemas.append("Se esperan al menos 2 escenarios (camino feliz y un error).")
    for i, bloque in enumerate(bloques, 1):
        for clave in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{clave}\b", bloque, flags=re.MULTILINE):
                problemas.append(f"El escenario {i} no tiene '{clave}'.")
    return problemas


# --- Casos de prueba (agente 2, diseñador de pruebas) ---------------------------
class CasoPrueba(BaseModel):
    id: str                          # CP-01, CP-02...
    escenario: str                   # nombre exacto del escenario Gherkin que cubre
    nivel: Literal["api", "e2e"]     # api: se prueba con HTTP; e2e: se prueba en el navegador
    precondiciones: list[str]
    pasos: list[str]
    datos: dict[str, str]            # todos los valores son texto: "201", no 201
    resultado_esperado: str


class PlanPruebas(BaseModel):
    historia: str
    casos: list[CasoPrueba]


def validar_plan(texto: str, gherkin: str) -> list[str]:
    """JSON que cumple el contrato y cada escenario cubierto por al menos un caso."""
    try:
        plan = PlanPruebas.model_validate_json(texto)
    except ValidationError as e:     # errores cortos y accionables: el agente los lee y corrige
        return ["El JSON no cumple el contrato: " + "; ".join(
            f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()[:5])]
    cubiertos = {c.escenario.strip() for c in plan.casos}
    problemas = [f"Escenario sin casos: {e}" for e in escenarios(gherkin) if e not in cubiertos]
    ids = [c.id for c in plan.casos]
    if len(ids) != len(set(ids)):
        problemas.append("Hay ids de caso repetidos.")
    return problemas


# --- Sesión 4 · filtro de seguridad y triage ---------------------------------------
class Veredicto(BaseModel):
    """Lo que entrega el subagente filtro-seguridad: ¿la historia trae instrucciones para un agente?"""
    sospechosa: bool
    motivo: str


class Diagnostico(BaseModel):
    """Lo que entrega el subagente triage: quién debe corregir una prueba fallida y por qué."""
    responsable: Literal["desarrollador", "automatizador", "despliegue"]
    causa: str          # qué falló, en una o dos frases
    criterio: str       # escenario de aceptación que se usa como referencia
    instruccion: str    # qué debe corregir el responsable


def validar_json(contrato: type[BaseModel], texto: str) -> list[str]:
    try:
        contrato.model_validate_json(texto)
        return []
    except ValidationError as e:
        return ["El JSON no cumple el contrato: " + "; ".join(
            f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()[:5])]