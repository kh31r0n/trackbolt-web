"""Asocia una imagen de referencia a cada producto, por tipo y no por codigo.

Las imagenes salen del catalogo PDF del fabricante (scripts/extraer_imagenes_pdf.py). Sus codigos
son del fabricante y no coinciden con los del ERP, asi que no hay forma de mapear referencia a
referencia: lo que se mapea es el *tipo* de pieza, es decir la pareja linea/grupo de la taxonomia,
y un mismo dibujo ilustra a todas las referencias de ese grupo.

El mapa vive en data/imagenes.json, se cura a mano con la hoja de contactos que deja el extractor,
y tiene dos niveles: `por_grupo` ("linea|grupo") y, como respaldo, `por_linea`. Lo que no esta
mapeado se queda sin imagen: es preferible una ficha sin dibujo que una con el dibujo equivocado.
"""
import json
from pathlib import Path


def cargar(ruta):
    """Devuelve el mapa {por_grupo, por_linea}. Ruta vacia o inexistente: mapa vacio."""
    vacio = {"por_grupo": {}, "por_linea": {}}
    if not ruta:
        return vacio
    ruta = Path(ruta)
    if not ruta.exists():
        return vacio
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return {
        "por_grupo": datos.get("por_grupo") or {},
        "por_linea": datos.get("por_linea") or {},
    }


def clave(linea, grupo):
    """La clave de `por_grupo`: la linea publica y el grupo, separados por barra."""
    return f"{linea}|{grupo}"


def para(mapa, linea, grupo):
    """Ruta publica de la imagen del producto, o None. El grupo manda sobre la linea."""
    if not mapa:
        return None
    imagen = mapa.get("por_grupo", {}).get(clave(linea, grupo))
    if imagen:
        return imagen
    return mapa.get("por_linea", {}).get(linea) or None
