"""Cálculo de la antigüedad de un empleado (HU-05). Funciones puras, sin base de datos."""
import os
from datetime import date


def fecha_hoy() -> date:
    """Fecha de «hoy». Si existe la variable de entorno FECHA_HOY (AAAA-MM-DD) se usa esa;
    así las pruebas contra la app desplegada son deterministas. Si no, la fecha del sistema."""
    texto = (os.environ.get("FECHA_HOY") or "").strip()
    if texto:
        try:
            return date.fromisoformat(texto)
        except ValueError:
            pass
    return date.today()


def calcular_antiguedad(ingreso: date, hasta: date) -> tuple[int, int]:
    """Años y meses completos entre ingreso y hasta. Un mes solo cuenta si está completo:
    si el día de 'hasta' es menor que el día de ingreso, el último mes no cuenta."""
    total = (hasta.year - ingreso.year) * 12 + (hasta.month - ingreso.month)
    if hasta.day < ingreso.day:
        total -= 1
    total = max(total, 0)
    return total // 12, total % 12


def texto_antiguedad(anios: int, meses: int) -> str:
    """Siempre «N años M meses», en plural, igual que los criterios."""
    return f"{anios} años {meses} meses"
