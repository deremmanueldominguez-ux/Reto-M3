"""Lista las preguntas abiertas que dejó el analista (las decide una persona, no un agente).

Uso:  python -m validadores.preguntas salida/HU-01/criterios.feature
Imprime una pregunta por línea; nada si no hay. Código de salida 0 siempre.
"""
import sys
from pathlib import Path

from validadores.contratos import preguntas_abiertas

if __name__ == "__main__":
    for pregunta in preguntas_abiertas(Path(sys.argv[1]).read_text(encoding="utf-8")):
        print("-", pregunta)