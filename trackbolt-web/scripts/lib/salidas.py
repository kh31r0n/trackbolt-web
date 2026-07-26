"""Escritura de los JSON que consume Astro."""
import json
from pathlib import Path


def escribir(destino, nombre, datos, compacto=False):
    ruta = Path(destino) / nombre
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if compacto:
        texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    else:
        texto = json.dumps(datos, ensure_ascii=False, indent=1)
    ruta.write_text(texto + "\n", encoding="utf-8")
    return ruta, len(texto.encode("utf-8"))


def kb(n):
    return f"{n / 1024:.0f} KB"
