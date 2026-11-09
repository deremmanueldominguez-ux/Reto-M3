"""Motor de base de datos y sesión de SQLAlchemy (SQLite en datos/empleados.db)."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

CARPETA_DATOS = Path(__file__).resolve().parent / "datos"
CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
RUTA_BD = CARPETA_DATOS / "empleados.db"

motor = create_engine(
    f"sqlite:///{RUTA_BD.as_posix()}",
    connect_args={"check_same_thread": False},
)
SesionLocal = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""


def obtener_sesion():
    """Dependencia de FastAPI: abre una sesión por petición y la cierra al terminar."""
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()


def crear_tablas() -> None:
    """Crea la carpeta de datos y las tablas que falten."""
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    import modelos  # noqa: F401  (registra los modelos en Base.metadata)

    Base.metadata.create_all(bind=motor)
