"""Corre una verificación desde la terminal (la usan /fabrica y hooks/compuerta.py; también tú).

Uso:  python -m verificacion app
      python -m verificacion pruebas HU-01      (sesión 3)
Código de salida 0 = pasó; 1 = falló (el log explica por qué).
"""
import sys

from verificacion import verificar

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python -m verificacion <nombre> [HU-xx]")
    ok, log = verificar(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(log)
    print("\nVERIFICACIÓN:", "OK" if ok else "FALLA")
    sys.exit(0 if ok else 1)