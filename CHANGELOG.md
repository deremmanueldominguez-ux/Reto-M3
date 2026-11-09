# Cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Sin publicar]

### Añadido

- `hooks/seguridad.py` · **Regla 5, autoprotección de las defensas.** Una historia envenenada ya no puede pedir
  al agente que modifique el propio hook, `settings.json` ni que vacíe la auditoría. Se bloquea (código 2):
  - Write/Edit/MultiEdit/NotebookEdit sobre `hooks/`, `.claude/settings.json`, `.claude/settings.local.json`
    o `auditoria.jsonl`.
  - Comandos Bash/PowerShell que nombran uno de esos archivos y además lo modifican (`>`, `rm`, `mv`, `cp`,
    `truncate`, `tee`, `sed -i`, `Set-Content`, `Clear-Content`, ...). Leerlos sigue permitido.
- Ejemplos para probar la regla sin modelo en el README («Probar los hooks sin modelo»).
- `hooks/seguridad.py` · **Sandbox de pruebas.** `ejecutar_pruebas_en_sandbox(origen, argumentos, variables, tiempo)`
  copia una carpeta de pruebas a un directorio temporal y corre pytest con `python -I`, entorno mínimo, sin
  autocarga de plugins (solo `pytest_playwright`) y tiempo límite. Cada corrida deja una línea
  `"herramienta": "sandbox"` en `auditoria.jsonl` (`permitida` si pasan, `bloqueada` si fallan).
  `ejecutar_en_sandbox(codigo, pruebas)` queda como atajo para un módulo y su archivo de pruebas.

### Cambiado

- `auditoria.jsonl` · cada línea trae `decision` (`"permitida"` o `"bloqueada"`) y, si se bloqueó, `motivo`.
  Antes se auditaba antes de revisar y no quedaba constancia de qué se decidió.
- `hooks/seguridad.py` · `bloquear()` lanza la excepción `Bloqueo` en vez de terminar el proceso, para que el
  intento se audite con su motivo antes de salir con código 2.
- `hooks/seguridad.py` · el señuelo se escribe como `"BANDERA" + "-DEMO"`, para que la regla 3 no impida
  editar el propio archivo.

- `verificacion/e2e.py` y `verificacion/pruebas.py` · las pruebas del automatizador (ejecución y recolección)
  corren en el sandbox en vez de en el proceso de la verificación. `e2e` borra el `resultados.xml` anterior
  antes de correr, para que el triage no lea resultados viejos.

### Pendiente

- Agregar `PowerShell` (y `NotebookEdit`) al matcher de `hooks/seguridad.py` en `.claude/settings.json`; hoy la
  regla 5 no revisa los comandos de PowerShell. Por la propia regla 5, este cambio lo hace una persona a mano.
