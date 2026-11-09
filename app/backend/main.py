"""Aplicación FastAPI de gestión de empleados. Expone `app`."""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Permite importar los módulos hermanos tanto con `uvicorn main:app` como con `app.backend.main:app`.
CARPETA_BACKEND = Path(__file__).resolve().parent
if str(CARPETA_BACKEND) not in sys.path:
    sys.path.insert(0, str(CARPETA_BACKEND))

from fastapi import APIRouter, FastAPI, Request  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

from database import crear_tablas  # noqa: E402
from rutas import departamentos, empleados  # noqa: E402


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    crear_tablas()
    yield


app = FastAPI(title="Gestión de empleados", lifespan=ciclo_de_vida)
crear_tablas()


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(_request: Request, exc: RequestValidationError):
    """Convierte los errores de Pydantic en {"detail": "Corrige el campo <campo>: <motivo>"}."""
    errores = exc.errors()
    if errores:
        primero = errores[0]
        ubicacion = [str(p) for p in primero.get("loc", []) if p not in ("body", "query", "path")]
        campo = ubicacion[0] if ubicacion else "solicitud"
        motivo = primero.get("msg", "valor inválido")
    else:
        campo, motivo = "solicitud", "valor inválido"
    return JSONResponse(status_code=422, content={"detail": f"Corrige el campo {campo}: {motivo}"})


api = APIRouter(prefix="/api")


@api.get("/salud")
def salud():
    return {"estado": "ok"}


api.include_router(departamentos.router)
api.include_router(empleados.router)
app.include_router(api)
