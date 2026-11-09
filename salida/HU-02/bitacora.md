# Bitácora · HU-02 Consultar el directorio de empleados

**Estado final: LISTA** (`python -m verificacion app` → VERIFICACIÓN: OK)

La verificación solo comprueba que el backend arranca (`GET /api/salud`) y que el frontend compila. Los casos e2e no se han ejecutado y la pantalla no se ha probado en un navegador.

## Pasos
1. Analista: sobrescribió `criterios.feature` con 9 escenarios.
2. Compuerta de criterios: válido.
3. Preguntas abiertas: 11. La persona decidió continuar.
4. Diseñador: escribió `casos_prueba.json` con 18 casos (9 api y 9 e2e). Validación: válido.
5. Plan: `plan.md` escrito. La persona lo aprobó sin comentarios (0 rechazos).
6. Desarrollador: modificó `rutas/empleados.py`, `api.js` y `App.jsx`, y creó `FiltrosDirectorio.jsx`. Según su informe, probó la API con TestClient y SQLite en memoria.
7. Verificación: OK al primer intento, sin ciclo de corrección.
8. Bitácora: escrita.

## Pendiente
- «Lopez» sí encuentra a Ana López: el plan dice lo contrario, pero la búsqueda también mira el correo, que no lleva acento. Ningún caso lo cubre; no se cambió.
- Si falla una búsqueda, sigue en pantalla la lista anterior, y `mensaje-error` no se limpia cuando la siguiente carga sale bien. Fuera del plan; no se cambió.
- Decisiones marcadas **[a revisar]** en `plan.md`.
- Los casos exigen una base vacía y `empleados.db` persiste: decidir si se respalda y se vacía.
- Los contenedores desplegados no se han reconstruido con estos cambios, y los casos de HU-02 no están automatizados en `app/tests/`.
