"""Catálogo de departamentos."""
from fastapi import APIRouter

from catalogos import DEPARTAMENTOS

router = APIRouter(prefix="/departamentos", tags=["departamentos"])


@router.get("")
def listar_departamentos() -> list[str]:
    return list(DEPARTAMENTOS)
