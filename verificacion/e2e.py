"""Sesión 4 · Corre TODAS las pruebas (API y E2E) contra la app desplegada y resume los fallos.

Las pruebas las escribió un agente: son código no revisado. Por eso no corren en el proceso de la
verificación sino en el sandbox de hooks/seguridad.py (`ejecutar_pruebas_en_sandbox`): copia de app/tests
en una carpeta temporal, intérprete aislado, entorno mínimo (solo URL_API y URL_WEB) y tiempo límite.
Cada ejecución deja su línea en auditoria.jsonl (herramienta "sandbox").

Deja dos archivos para el triage: salida/HU-xx/resultados.xml (JUnit) y salida/HU-xx/fallos.md (resumen).
"""
import xml.etree.ElementTree as ET

from hooks.seguridad import ejecutar_pruebas_en_sandbox
from verificacion.comun import APP, SALIDA

TIEMPO_E2E = 900   # segundos: Playwright abre un navegador por prueba


def verificar(hu: str | None = None) -> tuple[bool, str]:
    if not hu:
        return False, "Indica la historia: python -m verificacion e2e HU-01"
    carpeta = SALIDA / hu
    carpeta.mkdir(parents=True, exist_ok=True)
    reporte = carpeta / "resultados.xml"
    reporte.unlink(missing_ok=True)               # que no quede el JUnit de una corrida anterior
    variables = {"URL_API": "http://localhost:8000", "URL_WEB": "http://localhost:8080"}
    r = ejecutar_pruebas_en_sandbox(APP / "tests", ["-q", "--tb=short", f"--junitxml={reporte}"],
                                    variables, TIEMPO_E2E)
    fallos = []
    if reporte.exists():
        for caso in ET.parse(reporte).getroot().iter("testcase"):
            for problema in list(caso.findall("failure")) + list(caso.findall("error")):
                fallos.append(f"- {caso.get('classname')}::{caso.get('name')}\n  {(problema.get('message') or '')[:400]}")
    lineas = r["salida"].strip().splitlines()
    resumen = lineas[-1] if lineas else "sin salida"
    log = f"{resumen}\n" + "\n".join(fallos)
    (carpeta / "fallos.md").write_text(f"# Pruebas de {hu}\n\n{log}\n", encoding="utf-8")
    return r["ok"], log
