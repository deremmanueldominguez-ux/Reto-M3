"""Hook SubagentStop · El código decide cuándo terminó un agente (reflexión y evaluador con tope).

Claude Code llama a este script cuando un subagente quiere terminar. Si su entrega no pasa
el validador determinista, o si su verificación falla, respondemos {"decision": "block", "reason": ...}:
el subagente NO termina, recibe los problemas como instrucción y vuelve a intentarlo.

- Sesión 1: valida la ENTREGA (criterios.feature, casos_prueba.json) → patrón Reflexión.
- Sesión 2: además corre una VERIFICACIÓN (verificacion/app.py) → patrón Evaluador-optimizador:
  el desarrollador no termina hasta que el backend arranca y el frontend compila.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from hooks.roles import ROLES  # noqa: E402
from validadores.validar import problemas_de  # noqa: E402

ESTADO = RAIZ / "salida" / ".compuerta"           # cuántas veces hemos bloqueado a cada subagente


def tarea_del_subagente(transcripcion: str | None) -> str:
    """El primer mensaje de la transcripción del subagente es la tarea que recibió."""
    try:
        with open(transcripcion, encoding="utf-8") as f:
            for linea in f:
                d = json.loads(linea)
                if d.get("type") == "user":
                    contenido = d["message"]["content"]
                    return contenido if isinstance(contenido, str) else json.dumps(contenido)
    except (OSError, TypeError, ValueError, KeyError):
        pass
    return ""


def revisar(rol, hu: str) -> list[str]:
    problemas = []
    if rol.entrega:
        ruta = RAIZ / "salida" / hu / rol.entrega
        encontrados = problemas_de(ruta) if ruta.exists() else [f"No escribiste {ruta.relative_to(RAIZ)}."]
        if encontrados is None:                   # falla cerrado: una entrega sin validador nunca pasa sola
            encontrados = [f"La compuerta no sabe validar {rol.entrega}; agrega su validador en validadores/validar.py."]
        problemas += encontrados
    if rol.verifica and not problemas:
        try:                                      # falla cerrado: si la verificación se cae, nunca aprueba
            from verificacion import verificar   # se importa solo si hace falta (sesión 2 en adelante)
            ok, log = verificar(rol.verifica, hu)
        except Exception as error:
            ok, log = False, f"La verificación no pudo ejecutarse: {error!r}"
        if not ok:
            problemas.append(f"La verificación «{rol.verifica}» falló:\n{log[-3000:]}")
    return problemas


if __name__ == "__main__":
    datos = json.load(sys.stdin)
    agente = datos.get("agent_type")
    rol = ROLES.get(agente)
    hu = re.search(r"HU-\d+", tarea_del_subagente(datos.get("agent_transcript_path")))
    if not rol or not (rol.entrega or rol.verifica) or not hu:   # sin entrega asignada no hay nada que revisar
        sys.exit(0)

    problemas = revisar(rol, hu.group())
    if not problemas:
        sys.exit(0)                               # entrega válida: puede terminar

    ESTADO.mkdir(parents=True, exist_ok=True)
    contador = ESTADO / f"{datos.get('agent_id', agente)}.txt"
    intentos = int(contador.read_text()) if contador.exists() else 0
    if intentos >= rol.max_intentos:              # tope: dejamos terminar y avisamos a la persona
        print(json.dumps({"systemMessage": f"{agente}: {hu.group()} sigue sin pasar tras {rol.max_intentos} "
                                           "correcciones; escala a una persona:\n- " + "\n- ".join(problemas)},
                         ensure_ascii=False))
        sys.exit(0)
    contador.write_text(str(intentos + 1))
    print(json.dumps({"decision": "block", "reason":
                      f"La compuerta rechazó tu trabajo en {hu.group()} (corrección {intentos + 1} de "
                      f"{rol.max_intentos}). Corrige esto y vuelve a guardar:\n- " + "\n- ".join(problemas)},
                     ensure_ascii=False))