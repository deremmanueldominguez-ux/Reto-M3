"""Pruebas de API de la HU-05: consultar la antigüedad de cada empleado (pytest + httpx).

La app desplegada usa FECHA_HOY=2026-11-08 como «hoy». El número de empleado lo asigna el
sistema y la base persiste entre ejecuciones, así que cada prueba da de alta a sus empleados con
correos únicos (uuid) y los localiza por ese correo, sin asumir EMP-0001..EMP-0004.
"""
import uuid

import httpx

FECHA_HOY = "2026-11-08"


def correo_unico(prefijo: str) -> str:
    return f"{prefijo}.{uuid.uuid4().hex[:10]}@empresa.com"


def dar_de_alta(url_api: str, nombre: str, correo: str, fecha_ingreso: str) -> dict:
    """Crea un empleado activo y devuelve el cuerpo de la respuesta 201."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados",
        json={
            "nombre": nombre,
            "correo": correo,
            "puesto": "Analista",
            "departamento": "Tecnología",
            "fecha_ingreso": fecha_ingreso,
        },
        timeout=10,
    )
    assert respuesta.status_code == 201, respuesta.text
    creado = respuesta.json()
    assert creado["estado"].lower() == "activo"
    return creado


def comprobar_salud(url_api: str) -> None:
    respuesta = httpx.get(f"{url_api}/api/salud", timeout=10)
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json() == {"estado": "ok"}


def listar(url_api: str) -> list[dict]:
    respuesta = httpx.get(f"{url_api}/api/empleados", timeout=10)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def buscar_por_correo(empleados: list[dict], correo: str) -> dict:
    encontrados = [e for e in empleados if (e.get("correo") or "").lower() == correo.lower()]
    assert len(encontrados) == 1, f"Se esperaba un empleado con correo {correo}, hay {len(encontrados)}"
    return encontrados[0]


def test_cp01_antiguedad_en_anios_y_meses(url_api):
    """CP-01: Ver la antigüedad en años y meses de cada empleado (API)."""
    comprobar_salud(url_api)
    correo_1 = correo_unico("ana.perez")
    correo_2 = correo_unico("luis.gomez")
    creado_1 = dar_de_alta(url_api, "Ana Pérez", correo_1, "2024-05-08")
    creado_2 = dar_de_alta(url_api, "Luis Gómez", correo_2, "2021-11-08")

    empleados = listar(url_api)
    empleado_1 = buscar_por_correo(empleados, correo_1)
    empleado_2 = buscar_por_correo(empleados, correo_2)

    assert empleado_1["numero_empleado"] == creado_1["numero_empleado"]
    assert empleado_1["fecha_ingreso"] == "2024-05-08"
    assert empleado_1["antiguedad"] == "2 años 6 meses"
    assert empleado_2["numero_empleado"] == creado_2["numero_empleado"]
    assert empleado_2["fecha_ingreso"] == "2021-11-08"
    assert empleado_2["antiguedad"] == "5 años 0 meses"


def test_cp03_ingreso_hoy_antiguedad_cero(url_api):
    """CP-03: Empleado que ingresó hoy tiene antigüedad cero (API)."""
    comprobar_salud(url_api)
    correo = correo_unico("marta.ruiz")
    creado = dar_de_alta(url_api, "Marta Ruiz", correo, FECHA_HOY)

    empleado = buscar_por_correo(listar(url_api), correo)

    assert empleado["numero_empleado"] == creado["numero_empleado"]
    assert empleado["fecha_ingreso"] == FECHA_HOY
    assert empleado["antiguedad"] == "0 años 0 meses"


def test_cp05_aniversario_este_mes(url_api):
    """CP-05: Antigüedad de un empleado que cumple aniversario este mes (API)."""
    comprobar_salud(url_api)
    correo = correo_unico("carlos.diaz")
    creado = dar_de_alta(url_api, "Carlos Díaz", correo, "2016-11-08")

    empleado = buscar_por_correo(listar(url_api), correo)

    assert empleado["numero_empleado"] == creado["numero_empleado"]
    assert empleado["fecha_ingreso"] == "2016-11-08"
    assert empleado["antiguedad"] == "10 años 0 meses"
