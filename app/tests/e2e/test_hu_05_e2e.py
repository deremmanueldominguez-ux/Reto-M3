"""Pruebas de punta a punta de la HU-05: antigüedad en el directorio (pytest-playwright).

La app desplegada usa FECHA_HOY=2026-11-08 como «hoy». Cada prueba da de alta a sus empleados
por la API con correos únicos (uuid); el número de empleado y el id los asigna el sistema, así que
se toman de la respuesta del alta (no se asume EMP-0001..EMP-0004).
"""
import uuid

import httpx
from playwright.sync_api import Page, expect

FECHA_HOY = "2026-11-08"


def correo_unico(prefijo: str) -> str:
    return f"{prefijo}.{uuid.uuid4().hex[:10]}@empresa.com"


def dar_de_alta(url_api: str, nombre: str, prefijo_correo: str, fecha_ingreso: str) -> dict:
    """Crea un empleado activo y devuelve el cuerpo de la respuesta 201 (con id y numero_empleado)."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados",
        json={
            "nombre": nombre,
            "correo": correo_unico(prefijo_correo),
            "puesto": "Analista",
            "departamento": "Tecnología",
            "fecha_ingreso": fecha_ingreso,
        },
        timeout=10,
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def abrir_directorio(page: Page, url_web: str) -> None:
    page.goto(url_web)
    expect(page.get_by_test_id("tabla-empleados")).to_be_visible()


def comprobar_antiguedad(page: Page, empleado: dict, esperada: str) -> None:
    """Localiza la fila del empleado por su id y comprueba número y antigüedad."""
    identificador = empleado["id"]
    fila = page.get_by_test_id(f"fila-empleado-{identificador}")
    expect(fila).to_be_visible()
    expect(fila.get_by_test_id(f"numero-empleado-{identificador}")).to_have_text(empleado["numero_empleado"])
    expect(fila.get_by_test_id(f"antiguedad-empleado-{identificador}")).to_have_text(esperada)


def test_cp02_directorio_muestra_antiguedad(page: Page, url_web, url_api):
    """CP-02: Ver la antigüedad en años y meses de cada empleado (pantalla)."""
    ana = dar_de_alta(url_api, "Ana Pérez", "ana.perez", "2024-05-08")
    luis = dar_de_alta(url_api, "Luis Gómez", "luis.gomez", "2021-11-08")

    abrir_directorio(page, url_web)

    comprobar_antiguedad(page, ana, "2 años 6 meses")
    comprobar_antiguedad(page, luis, "5 años 0 meses")


def test_cp04_ingreso_hoy_muestra_cero(page: Page, url_web, url_api):
    """CP-04: Empleado que ingresó hoy tiene antigüedad cero (pantalla)."""
    marta = dar_de_alta(url_api, "Marta Ruiz", "marta.ruiz", FECHA_HOY)

    abrir_directorio(page, url_web)

    comprobar_antiguedad(page, marta, "0 años 0 meses")


def test_cp06_aniversario_este_mes(page: Page, url_web, url_api):
    """CP-06: Antigüedad de un empleado que cumple aniversario este mes (pantalla)."""
    carlos = dar_de_alta(url_api, "Carlos Díaz", "carlos.diaz", "2016-11-08")

    abrir_directorio(page, url_web)

    comprobar_antiguedad(page, carlos, "10 años 0 meses")
