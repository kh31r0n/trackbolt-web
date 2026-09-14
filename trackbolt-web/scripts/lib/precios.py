"""Niveles de precio.

La lista de importación trae el precio mayorista (`PRECIO UNIT`); de él se derivan los otros
tres niveles. Para las referencias sin precio en la lista, la base es el costo promedio del ERP.
"""

# Multiplicadores heredados de transform_catalogo.py.
MULTIPLICADORES = {
    "mostrador": 2.5,
    "usuario_final": 2.0,
    "almacen": 1.75,
    "mayorista": 1.5,
}

ETIQUETAS = {
    "mostrador": "Mostrador",
    "usuario_final": "Usuario final",
    "almacen": "Almacén",
    "mayorista": "Mayorista",
}


def redondear(valor, multiplo=0):
    """Con multiplo > 1, redondeo comercial a ese múltiplo de COP; si no, a centavos."""
    if valor is None:
        return None
    if multiplo is None or multiplo <= 1:
        return round(valor, 2)
    return int(round(valor / multiplo) * multiplo)


def calcular(promedio, multiplo=0, mayorista=None):
    """Devuelve los niveles. Si hay precio mayorista, la base sale de él; si no, del costo
    promedio. Sin base positiva no hay precio confiable y se devuelve {}."""
    if mayorista is not None and mayorista > 0:
        base = mayorista / MULTIPLICADORES["mayorista"]
    else:
        base = promedio
    if base is None or base <= 0:
        return {}
    return {n: redondear(base * m, multiplo) for n, m in MULTIPLICADORES.items()}
