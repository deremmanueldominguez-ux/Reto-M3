# Bitácora · HU-03 Editar y dar de baja a un empleado

**Estado final: LISTA** (`python -m verificacion app` → VERIFICACIÓN: OK)

La verificación solo comprueba que el backend arranca (`GET /api/salud`) y que el frontend compila. Los casos e2e no se han ejecutado y la interfaz no se ha abierto en un navegador.

## Pasos
1. Analista: guardó `criterios.feature` con 11 escenarios; según su informe, con el mismo contenido.
2. Compuerta de criterios: válido.
3. Preguntas abiertas: 13. La persona decidió continuar.
4. Diseñador: no reescribió `casos_prueba.json`; lo dejó con 21 casos (11 api y 10 e2e). Validación: válido.
5. Plan: el arquitecto sobrescribió `plan.md` con una propuesta sin cambios de código, tras revisar sin ejecutar. La persona lo aprobó sin comentarios (0 rechazos).
6. Desarrollador: no cambió código fuente. Según su informe, los 11 casos de API pasan con TestClient y SQLite en memoria, y `npm run build` regeneró `app/frontend/dist`.
7. Verificación: OK al primer intento, sin ciclo de corrección.
8. Bitácora: escrita; sustituye a la de la ejecución anterior, que también terminó en LISTA.

## Pendiente
- `app/tests/` no tiene pruebas de HU-03 y los 10 casos e2e solo se revisaron leyendo el código.
- Decisiones marcadas **[a revisar]** en `plan.md`, incluida la baja con fecha futura, que cambia el estado de inmediato.
- Regla 6: un cuerpo inválido enviado a un empleado de baja responde 422 y no 409. Ningún caso combina esas condiciones.
- Los casos e2e exigen una base vacía y `empleados.db` persiste: decidir si se respalda y se vacía.
- Los contenedores desplegados pueden no incluir este código.
