"""Recurso /api/empleados."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from catalogos import ESTADO_ACTIVO
from database import obtener_sesion
from esquemas import MENSAJE_CORREO_DUPLICADO, EmpleadoCrear, EmpleadoSalida, validar_alta
from modelos import Empleado

router = APIRouter(prefix="/empleados", tags=["empleados"])


def siguiente_numero_empleado(sesion: Session) -> str:
    """EMP- + (máximo consecutivo existente + 1). Cuenta también las bajas: no se reutiliza."""
    maximo = 0
    for numero in sesion.scalars(select(Empleado.numero_empleado)):
        try:
            maximo = max(maximo, int(numero.split("-", 1)[1]))
        except (IndexError, ValueError):
            continue
    return f"EMP-{maximo + 1:04d}"


@router.get("", response_model=list[EmpleadoSalida])
def listar_empleados(sesion: Session = Depends(obtener_sesion)):
    return sesion.scalars(select(Empleado).order_by(Empleado.id)).all()


@router.post("", response_model=EmpleadoSalida, status_code=201)
def registrar_empleado(datos: EmpleadoCrear, sesion: Session = Depends(obtener_sesion)):
    valores = validar_alta(datos)

    existe = sesion.scalar(
        select(func.count()).select_from(Empleado).where(func.lower(Empleado.correo) == valores["correo"])
    )
    if existe:
        raise HTTPException(status_code=409, detail=MENSAJE_CORREO_DUPLICADO)

    empleado = Empleado(
        **valores,
        numero_empleado=siguiente_numero_empleado(sesion),
        estado=ESTADO_ACTIVO,
        fecha_baja=None,
        creado_en=datetime.now(),
    )
    sesion.add(empleado)
    try:
        sesion.commit()
    except IntegrityError:
        sesion.rollback()
        raise HTTPException(status_code=409, detail=MENSAJE_CORREO_DUPLICADO)
    sesion.refresh(empleado)
    return empleado
