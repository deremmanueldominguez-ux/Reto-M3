"""Pruebas de punta a punta de la HU-01: registrar empleado (pytest-playwright).

Cada prueba usa correos únicos (uuid). El número de empleado esperado se calcula con la API
(máximo existente + 1) porque la base de datos no se reinicia entre ejecuciones.
"""
import json
import re
import uuid

import httpx
from playwright.sync_api import Page, Route, expect

PATRON_NUMERO = re.compile(r"^EMP-(\d{4,})$")
CAMPOS_FORMULARIO = [
    "empleado-nombre",
    "empleado-correo",
    "empleado-puesto",
    "empleado-departamento",
    "empleado-fecha-ingreso",
]
DEPARTAMENTOS = ["Tecnología", "Ventas", "Finanzas", "Recursos Humanos", "Operaciones"]


def correo_unico(prefijo: str, dominio: str = "empresa.com") -> str:
    return f"{prefijo}.{uuid.uuid4().hex[:10]}@{dominio}"


def listar(url_api: str) -> list[dict]:
    respuesta = httpx.get(f"{url_api}/api/empleados", timeout=10)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def con_correo(url_api: str, correo: str) -> list[dict]:
    return [e for e in listar(url_api) if (e.get("correo") or "").lower() == correo.lower()]


def siguiente_numero_esperado(url_api: str) -> str:
    maximo = 0
    for empleado in listar(url_api):
        coincidencia = PATRON_NUMERO.match(empleado.get("numero_empleado") or "")
        if coincidencia:
            maximo = max(maximo, int(coincidencia.group(1)))
    return f"EMP-{maximo + 1:04d}"


def abrir_formulario(page: Page, url_web: str) -> None:
    page.goto(url_web)
    expect(page.get_by_test_id("empleado-guardar")).to_be_visible()
    # Esperar a que el catálogo de departamentos se cargue en el selector.
    expect(page.get_by_test_id("empleado-departamento").locator("option").first).to_be_attached()


def llenar_formulario(page: Page, nombre: str, correo: str, puesto: str, departamento: str, fecha: str) -> None:
    page.get_by_test_id("empleado-nombre").fill(nombre)
    page.get_by_test_id("empleado-correo").fill(correo)
    page.get_by_test_id("empleado-puesto").fill(puesto)
    page.get_by_test_id("empleado-departamento").select_option(departamento)
    page.get_by_test_id("empleado-fecha-ingreso").fill(fecha)


def comprobar_error(page: Page, texto: str) -> None:
    error = page.get_by_test_id("mensaje-error")
    expect(error).to_be_visible()
    expect(error).to_contain_text(texto)
    expect(page.get_by_test_id("mensaje-exito")).to_have_count(0)


def test_cp02_registro_exitoso_muestra_numero(page: Page, url_web, url_api):
    """CP-02: Registro exitoso de un empleado con número asignado por el sistema (pantalla)."""
    correo = correo_unico("ana.lopez")
    abrir_formulario(page, url_web)
    esperado = siguiente_numero_esperado(url_api)

    llenar_formulario(page, "Ana López", correo, "Analista de Datos", "Tecnología", "2024-03-15")
    page.get_by_test_id("empleado-guardar").click()

    exito = page.get_by_test_id("mensaje-exito")
    expect(exito).to_be_visible()
    expect(exito).to_contain_text(esperado)
    expect(page.get_by_test_id("mensaje-error")).to_have_count(0)
    guardados = con_correo(url_api, correo)
    assert len(guardados) == 1
    assert guardados[0]["numero_empleado"] == esperado


def test_cp04_formulario_sin_campo_numero_empleado(page: Page, url_web):
    """CP-04: El formulario de registro no permite escribir el número de empleado."""
    abrir_formulario(page, url_web)

    for testid in CAMPOS_FORMULARIO:
        expect(page.get_by_test_id(testid)).to_be_visible()
    expect(page.get_by_test_id("empleado-guardar")).to_be_visible()

    formulario = page.locator("form").filter(has=page.get_by_test_id("empleado-guardar"))
    editables = formulario.locator("input, select, textarea")
    testids = sorted(editables.evaluate_all("els => els.map(e => e.getAttribute('data-testid'))"))
    assert testids == sorted(CAMPOS_FORMULARIO), f"Campos editables inesperados: {testids}"
    expect(formulario.locator("[data-testid*='numero-empleado']")).to_have_count(0)
    expect(formulario.locator("[name*='numero_empleado'], [id*='numero_empleado']")).to_have_count(0)


def test_cp07_correo_duplicado_muestra_error(page: Page, url_web, url_api):
    """CP-07: Correo duplicado sin importar mayúsculas (pantalla)."""
    correo = correo_unico("ana.lopez")
    previo = httpx.post(
        f"{url_api}/api/empleados",
        json={
            "nombre": "Ana López",
            "correo": correo,
            "puesto": "Analista de Datos",
            "departamento": "Tecnología",
            "fecha_ingreso": "2024-03-15",
        },
        timeout=10,
    )
    assert previo.status_code == 201, previo.text
    usuario, dominio = correo.split("@")

    abrir_formulario(page, url_web)
    llenar_formulario(page, "Ana Lopez", f"{usuario.upper()}@{dominio}", "Contadora", "Finanzas", "2024-02-01")
    page.get_by_test_id("empleado-guardar").click()

    comprobar_error(page, "El correo ya está registrado")
    assert len(con_correo(url_api, correo)) == 1


def test_cp09_correo_no_corporativo_muestra_error(page: Page, url_web, url_api):
    """CP-09: Correo que no es corporativo (pantalla)."""
    correo = correo_unico("luis.perez", "gmail.com")
    abrir_formulario(page, url_web)
    llenar_formulario(page, "Luis Pérez", correo, "Supervisor", "Operaciones", "2024-05-20")
    page.get_by_test_id("empleado-guardar").click()

    comprobar_error(page, "Usa el correo corporativo @empresa.com")
    assert not con_correo(url_api, correo)


def test_cp11_fecha_futura_muestra_error(page: Page, url_web, url_api):
    """CP-11: Fecha de ingreso futura (pantalla)."""
    correo = correo_unico("marta.diaz")
    abrir_formulario(page, url_web)
    llenar_formulario(page, "Marta Díaz", correo, "Reclutadora", "Recursos Humanos", "2099-01-01")
    page.get_by_test_id("empleado-guardar").click()

    comprobar_error(page, "La fecha de ingreso no puede ser futura")
    assert not con_correo(url_api, correo)


def test_cp13_nombre_corto_muestra_error(page: Page, url_web, url_api):
    """CP-13: Nombre demasiado corto (pantalla)."""
    correo = correo_unico("x.gomez")
    abrir_formulario(page, url_web)
    llenar_formulario(page, "X", correo, "Desarrollador", "Tecnología", "2024-04-01")
    page.get_by_test_id("empleado-guardar").click()

    comprobar_error(page, "nombre")
    assert not con_correo(url_api, correo)


def test_cp15_puesto_vacio_muestra_error(page: Page, url_web, url_api):
    """CP-15: Puesto vacío (pantalla)."""
    correo = correo_unico("elena.vega")
    abrir_formulario(page, url_web)
    llenar_formulario(page, "Elena Vega", correo, "", "Finanzas", "2024-04-01")
    page.get_by_test_id("empleado-guardar").click()

    comprobar_error(page, "puesto")
    assert not con_correo(url_api, correo)


def test_cp17_departamento_no_permitido_muestra_error(page: Page, url_web, url_api):
    """CP-17: Departamento que no está en la lista permitida (pantalla, valor forzado)."""
    correo = correo_unico("jorge.mora")
    abrir_formulario(page, url_web)

    opciones = page.get_by_test_id("empleado-departamento").locator("option")
    expect(opciones).to_have_count(len(DEPARTAMENTOS))
    textos = [t.strip() for t in opciones.all_inner_texts()]
    assert sorted(textos) == sorted(DEPARTAMENTOS)
    assert "Marketing" not in textos

    # Forzar "Marketing" interceptando la petición de alta (el selector no lo ofrece).
    def forzar_departamento(route: Route) -> None:
        if route.request.method == "POST":
            cuerpo = json.loads(route.request.post_data or "{}")
            cuerpo["departamento"] = "Marketing"
            route.continue_(post_data=json.dumps(cuerpo))
        else:
            route.continue_()

    page.route("**/api/empleados", forzar_departamento)

    llenar_formulario(page, "Jorge Mora", correo, "Diseñador", "Tecnología", "2024-04-01")
    page.get_by_test_id("empleado-guardar").click()

    comprobar_error(page, "departamento")
    assert not con_correo(url_api, correo)


def test_cp19_fecha_vacia_muestra_error(page: Page, url_web, url_api):
    """CP-19: Fecha de ingreso sin informar (pantalla)."""
    correo = correo_unico("sofia.rios")
    abrir_formulario(page, url_web)
    llenar_formulario(page, "Sofía Ríos", correo, "Operaria", "Operaciones", "")
    page.get_by_test_id("empleado-guardar").click()

    comprobar_error(page, "fecha_ingreso")
    assert not con_correo(url_api, correo)
