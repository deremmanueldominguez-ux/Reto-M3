"""Sesión 3 · ¿Las pruebas que escribió el automatizador se pueden recolectar y cubren cada caso?

Trazabilidad: cada id de salida/HU-xx/casos_prueba.json (CP-01, CP-02...) debe aparecer en algún test.
No ejecuta las pruebas contra la app: eso es la verificación e2e (sesión 4).

Recolectar ya importa los módulos de prueba (código escrito por un agente), así que también se hace en el
sandbox de hooks/seguridad.py. Es la verificación que la compuerta exige al automatizador.
"""
from hooks.seguridad import ejecutar_pruebas_en_sandbox
from validadores.contratos import PlanPruebas
from verificacion.comun import APP, SALIDA

TIEMPO_RECOLECCION = 120


def verificar(hu: str | None = None) -> tuple[bool, str]:
    if not hu:
        return False, "Indica la historia: python -m verificacion pruebas HU-01"
    casos = SALIDA / hu / "casos_prueba.json"
    if not casos.exists():
        return False, f"No existe {casos.relative_to(SALIDA.parent)}"
    r = ejecutar_pruebas_en_sandbox(APP / "tests", ["--collect-only", "-q"], tiempo=TIEMPO_RECOLECCION)
    ok, log = r["ok"], r["salida"]
    if not ok:
        return False, log
    ids = [c.id for c in PlanPruebas.model_validate_json(casos.read_text(encoding="utf-8")).casos]
    texto = "".join(p.read_text(encoding="utf-8") for p in (APP / "tests").rglob("test_*.py"))
    faltan = [i for i in ids if i not in texto]
    return not faltan, log if not faltan else f"Casos sin test: {', '.join(faltan)}"