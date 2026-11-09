"""Modelos de SQLAlchemy."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from catalogos import ESTADO_ACTIVO
from database import Base


class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_empleado: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    correo: Mapped[str] = mapped_column(String(254), unique=True, nullable=False, index=True)
    puesto: Mapped[str] = mapped_column(String(60), nullable=False)
    departamento: Mapped[str] = mapped_column(String(40), nullable=False)
    fecha_ingreso: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(String(10), nullable=False, default=ESTADO_ACTIVO)
    fecha_baja: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
