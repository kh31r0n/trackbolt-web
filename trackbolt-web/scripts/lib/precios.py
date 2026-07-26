"""Niveles de precio. El Excel trae el COSTO promedio; aqui se calcula la venta."""

# Multiplicadores heredados de transform_catalogo.py.
MULTIPLICADORES = {
    "mostrador": 2.5,
    "usuario_final": 2.0,
    "almacen": 1.75,
    "mayorista": 1.5,
}

# El precio que ve el publico corresponde al nivel usuario final.
NIVEL_PUBLICO = "usuario_final"

ETIQUETAS = {
    "mostrador": "Mostrador",
    "usuario_final": "Usuario final",
    "almacen": "Almacén",
    "mayorista": "Mayorista",
}


def redondear(valor, multiplo=50):
    """Redondeo comercial: los precios en COP no se publican con centavos."""
    if valor is None:
        return None
    return int(round(valor / multiplo) * multiplo)


def calcular(promedio, multiplo=50):
    """Devuelve (precio_publico, niveles). Si el costo es <= 0, no hay precio confiable."""
    if promedio is None or promedio <= 0:
        return None, {}
    niveles = {n: redondear(promedio * m, multiplo) for n, m in MULTIPLICADORES.items()}
    return niveles[NIVEL_PUBLICO], niveles
