"""Esquemas de Pydantic y validación de las reglas de negocio de entrada."""
import re
from datetime import date, datetime

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, computed_field

from antiguedad import calcular_antiguedad, fecha_hoy, texto_antiguedad
from catalogos import DEPARTAMENTOS, DOMINIO_CORREO, ESTADO_BAJA

MENSAJE_CORREO_CORPORATIVO = "Usa el correo corporativo @empresa.com"
MENSAJE_FECHA_FUTURA = "La fecha de ingreso no puede ser futura"
MENSAJE_CORREO_DUPLICADO = "El correo ya está registrado"

PATRON_CORREO = re.compile(r"^[^@\s]+" + re.escape(DOMINIO_CORREO) + r"$")


class EmpleadoCrear(BaseModel):
    """Datos que acepta el alta. Cualquier otro campo (p. ej. numero_empleado) se ignora."""

    model_config = ConfigDict(extra="ignore")

    nombre: str | None = None
    correo: str | None = None
    puesto: str | None = None
    departamento: str | None = None
    fecha_ingreso: str | None = None


class EmpleadoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date
    estado: str
    fecha_baja: date | None = None
    creado_en: datetime

    # HU-05: antigüedad calculada al responder (no se guarda). Para una baja se cuenta hasta fecha_baja.
    def _antiguedad(self) -> tuple[int, int]:
        hasta = self.fecha_baja if (self.estado == ESTADO_BAJA and self.fecha_baja) else fecha_hoy()
        return calcular_antiguedad(self.fecha_ingreso, hasta)

    @computed_field
    @property
    def antiguedad_anios(self) -> int:
        return self._antiguedad()[0]

    @computed_field
    @property
    def antiguedad_meses(self) -> int:
        return self._antiguedad()[1]

    @computed_field
    @property
    def antiguedad(self) -> str:
        return texto_antiguedad(*self._antiguedad())


def error_campo(campo: str, motivo: str) -> HTTPException:
    """Error 422 que indica qué campo corregir (regla 3)."""
    return HTTPException(status_code=422, detail=f"Corrige el campo {campo}: {motivo}")


def _limpiar(valor: str | None) -> str:
    return (valor or "").strip()


def validar_texto(campo: str, valor: str | None, minimo: int, maximo: int) -> str:
    texto = _limpiar(valor)
    if not texto:
        raise error_campo(campo, "es obligatorio")
    if not (minimo <= len(texto) <= maximo):
        raise error_campo(campo, f"debe tener entre {minimo} y {maximo} caracteres")
    return texto


def validar_departamento(valor: str | None) -> str:
    departamento = _limpiar(valor)
    if not departamento:
        raise error_campo("departamento", "es obligatorio")
    if departamento not in DEPARTAMENTOS:
        raise error_campo("departamento", "debe ser uno de: " + ", ".join(DEPARTAMENTOS))
    return departamento


def validar_correo(valor: str | None) -> str:
    correo = _limpiar(valor).lower()
    if not correo:
        raise error_campo("correo", "es obligatorio")
    if not PATRON_CORREO.match(correo):
        raise HTTPException(status_code=422, detail=MENSAJE_CORREO_CORPORATIVO)
    return correo


def validar_fecha_ingreso(valor: str | None) -> date:
    texto = _limpiar(valor)
    if not texto:
        raise error_campo("fecha_ingreso", "es obligatoria")
    try:
        fecha = date.fromisoformat(texto)
    except ValueError:
        raise error_campo("fecha_ingreso", "usa el formato AAAA-MM-DD")
    if fecha > fecha_hoy():
        raise HTTPException(status_code=422, detail=MENSAJE_FECHA_FUTURA)
    return fecha


def validar_alta(datos: EmpleadoCrear) -> dict:
    """Valida el alta en el orden acordado en el plan y devuelve los datos normalizados."""
    correo = validar_correo(datos.correo)
    fecha_ingreso = validar_fecha_ingreso(datos.fecha_ingreso)
    nombre = validar_texto("nombre", datos.nombre, 2, 80)
    puesto = validar_texto("puesto", datos.puesto, 2, 60)
    departamento = validar_departamento(datos.departamento)
    return {
        "nombre": nombre,
        "correo": correo,
        "puesto": puesto,
        "departamento": departamento,
        "fecha_ingreso": fecha_ingreso,
    }
