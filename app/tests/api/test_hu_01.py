"""Pruebas de API de la HU-01: registrar empleado.

Cada prueba usa correos únicos (uuid) para poder repetirse sin choques. Como la base de datos
no se reinicia entre ejecuciones, el número de empleado esperado se calcula a partir del
máximo existente (+1) en lugar de suponer «EMP-0008».
"""
import re
import uuid

import httpx
import pytest

PATRON_NUMERO = re.compile(r"^EMP-(\d{4,})$")


@pytest.fixture
def cliente(url_api):
    with httpx.Client(base_url=url_api, timeout=10) as cliente:
        yield cliente


def correo_unico(prefijo: str, dominio: str = "empresa.com") -> str:
    return f"{prefijo}.{uuid.uuid4().hex[:10]}@{dominio}"


def listar(cliente: httpx.Client) -> list[dict]:
    respuesta = cliente.get("/api/empleados")
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def siguiente_numero_esperado(empleados: list[dict]) -> str:
    maximo = 0
    for empleado in empleados:
        coincidencia = PATRON_NUMERO.match(empleado.get("numero_empleado") or "")
        if coincidencia:
            maximo = max(maximo, int(coincidencia.group(1)))
    return f"EMP-{maximo + 1:04d}"


def buscar_por_correo(empleados: list[dict], correo: str) -> list[dict]:
    return [e for e in empleados if (e.get("correo") or "").lower() == correo.lower()]


def comprobar_error_campo(respuesta: httpx.Response, campo: str) -> None:
    assert respuesta.status_code == 422, respuesta.text
    detalle = respuesta.json().get("detail")
    assert campo in str(detalle), f"El error no menciona el campo {campo}: {detalle}"


def test_cp01_registro_exitoso_numero_asignado(cliente):
    """CP-01: Registro exitoso de un empleado con número asignado por el sistema."""
    assert cliente.get("/api/salud").json() == {"estado": "ok"}
    correo = correo_unico("ana.lopez")
    previos = listar(cliente)
    assert not buscar_por_correo(previos, correo)
    esperado = siguiente_numero_esperado(previos)

    cuerpo = {
        "nombre": "Ana López",
        "correo": correo,
        "puesto": "Analista de Datos",
        "departamento": "Tecnología",
        "fecha_ingreso": "2024-03-15",
    }
    respuesta = cliente.post("/api/empleados", json=cuerpo)

    assert respuesta.status_code == 201, respuesta.text
    creado = respuesta.json()
    assert creado["numero_empleado"] == esperado
    assert creado["estado"] == "activo"
    assert creado.get("creado_en")

    encontrados = buscar_por_correo(listar(cliente), correo)
    assert len(encontrados) == 1
    guardado = encontrados[0]
    for campo, valor in cuerpo.items():
        assert guardado[campo] == valor
    assert guardado["numero_empleado"] == esperado


def test_cp03_numero_empleado_del_cliente_se_ignora(cliente):
    """CP-03: El formulario de registro no permite escribir el número de empleado (API ignora numero_empleado)."""
    correo = correo_unico("pedro.salas")
    previos = listar(cliente)
    esperado = siguiente_numero_esperado(previos)
    hay_9999_antes = any(e["numero_empleado"] == "EMP-9999" for e in previos)

    respuesta = cliente.post(
        "/api/empleados",
        json={
            "numero_empleado": "EMP-9999",
            "nombre": "Pedro Salas",
            "correo": correo,
            "puesto": "Técnico de Soporte",
            "departamento": "Tecnología",
            "fecha_ingreso": "2024-06-03",
        },
    )

    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["numero_empleado"] == esperado
    assert respuesta.json()["numero_empleado"] != "EMP-9999"
    empleados = listar(cliente)
    if not hay_9999_antes:
        assert not any(e["numero_empleado"] == "EMP-9999" for e in empleados)
    assert buscar_por_correo(empleados, correo)[0]["numero_empleado"] == esperado


def test_cp05_correo_se_guarda_en_minusculas(cliente):
    """CP-05: El correo se guarda en minúsculas."""
    sufijo = uuid.uuid4().hex[:10]
    correo_enviado = f"Carlos.Ruiz.{sufijo.upper()}@Empresa.com"
    correo_esperado = correo_enviado.lower()

    respuesta = cliente.post(
        "/api/empleados",
        json={
            "nombre": "Carlos Ruiz",
            "correo": correo_enviado,
            "puesto": "Vendedor",
            "departamento": "Ventas",
            "fecha_ingreso": "2024-01-10",
        },
    )

    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["correo"] == correo_esperado
    guardados = [e for e in listar(cliente) if e["id"] == respuesta.json()["id"]]
    assert len(guardados) == 1
    assert guardados[0]["correo"] == correo_esperado


def test_cp06_correo_duplicado_sin_importar_mayusculas(cliente):
    """CP-06: Correo duplicado sin importar mayúsculas."""
    correo = correo_unico("ana.lopez")
    previo = cliente.post(
        "/api/empleados",
        json={
            "nombre": "Ana López",
            "correo": correo,
            "puesto": "Analista de Datos",
            "departamento": "Tecnología",
            "fecha_ingreso": "2024-03-15",
        },
    )
    assert previo.status_code == 201, previo.text
    total_antes = len(listar(cliente))

    usuario, dominio = correo.split("@")
    respuesta = cliente.post(
        "/api/empleados",
        json={
            "nombre": "Ana Lopez",
            "correo": f"{usuario.upper()}@{dominio}",
            "puesto": "Contadora",
            "departamento": "Finanzas",
            "fecha_ingreso": "2024-02-01",
        },
    )

    assert respuesta.status_code == 409, respuesta.text
    assert respuesta.json() == {"detail": "El correo ya está registrado"}
    empleados = listar(cliente)
    assert len(empleados) == total_antes
    assert len(buscar_por_correo(empleados, correo)) == 1


def test_cp08_correo_no_corporativo(cliente):
    """CP-08: Correo que no es corporativo."""
    correo = correo_unico("luis.perez", "gmail.com")
    total_antes = len(listar(cliente))

    respuesta = cliente.post(
        "/api/empleados",
        json={
            "nombre": "Luis Pérez",
            "correo": correo,
            "puesto": "Supervisor",
            "departamento": "Operaciones",
            "fecha_ingreso": "2024-05-20",
        },
    )

    assert respuesta.status_code == 422, respuesta.text
    assert respuesta.json() == {"detail": "Usa el correo corporativo @empresa.com"}
    empleados = listar(cliente)
    assert len(empleados) == total_antes
    assert not buscar_por_correo(empleados, correo)


def test_cp10_fecha_ingreso_futura(cliente):
    """CP-10: Fecha de ingreso futura."""
    correo = correo_unico("marta.diaz")
    total_antes = len(listar(cliente))

    respuesta = cliente.post(
        "/api/empleados",
        json={
            "nombre": "Marta Díaz",
            "correo": correo,
            "puesto": "Reclutadora",
            "departamento": "Recursos Humanos",
            "fecha_ingreso": "2099-01-01",
        },
    )

    assert respuesta.status_code == 422, respuesta.text
    assert respuesta.json() == {"detail": "La fecha de ingreso no puede ser futura"}
    empleados = listar(cliente)
    assert len(empleados) == total_antes
    assert not buscar_por_correo(empleados, correo)


def test_cp12_nombre_demasiado_corto(cliente):
    """CP-12: Nombre demasiado corto."""
    correo = correo_unico("x.gomez")
    total_antes = len(listar(cliente))

    respuesta = cliente.post(
        "/api/empleados",
        json={
            "nombre": "X",
            "correo": correo,
            "puesto": "Desarrollador",
            "departamento": "Tecnología",
            "fecha_ingreso": "2024-04-01",
        },
    )

    comprobar_error_campo(respuesta, "nombre")
    empleados = listar(cliente)
    assert len(empleados) == total_antes
    assert not buscar_por_correo(empleados, correo)


def test_cp14_puesto_vacio(cliente):
    """CP-14: Puesto vacío."""
    correo = correo_unico("elena.vega")
    total_antes = len(listar(cliente))

    respuesta = cliente.post(
        "/api/empleados",
        json={
            "nombre": "Elena Vega",
            "correo": correo,
            "puesto": "",
            "departamento": "Finanzas",
            "fecha_ingreso": "2024-04-01",
        },
    )

    comprobar_error_campo(respuesta, "puesto")
    empleados = listar(cliente)
    assert len(empleados) == total_antes
    assert not buscar_por_correo(empleados, correo)


def test_cp16_departamento_no_permitido(cliente):
    """CP-16: Departamento que no está en la lista permitida."""
    departamentos = cliente.get("/api/departamentos")
    assert departamentos.status_code == 200, departamentos.text
    assert set(departamentos.json()) == {"Tecnología", "Ventas", "Finanzas", "Recursos Humanos", "Operaciones"}
    assert "Marketing" not in departamentos.json()

    correo = correo_unico("jorge.mora")
    total_antes = len(listar(cliente))

    respuesta = cliente.post(
        "/api/empleados",
        json={
            "nombre": "Jorge Mora",
            "correo": correo,
            "puesto": "Diseñador",
            "departamento": "Marketing",
            "fecha_ingreso": "2024-04-01",
        },
    )

    comprobar_error_campo(respuesta, "departamento")
    empleados = listar(cliente)
    assert len(empleados) == total_antes
    assert not buscar_por_correo(empleados, correo)


def test_cp18_fecha_ingreso_sin_informar(cliente):
    """CP-18: Fecha de ingreso sin informar (campo ausente y cadena vacía)."""
    correo = correo_unico("sofia.rios")
    total_antes = len(listar(cliente))
    base = {
        "nombre": "Sofía Ríos",
        "correo": correo,
        "puesto": "Operaria",
        "departamento": "Operaciones",
    }

    sin_campo = cliente.post("/api/empleados", json=base)
    comprobar_error_campo(sin_campo, "fecha_ingreso")

    vacio = cliente.post("/api/empleados", json={**base, "fecha_ingreso": ""})
    comprobar_error_campo(vacio, "fecha_ingreso")

    empleados = listar(cliente)
    assert len(empleados) == total_antes
    assert not buscar_por_correo(empleados, correo)
