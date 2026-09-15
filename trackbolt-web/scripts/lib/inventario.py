"""Combina dos reportes de existencias del ERP en un solo inventario.

El reporte base ('inventario total … .xlsx') es el unico que trae la linea REX. El reporte
adicional ('existencias adicionales … .xlsx') es una extraccion posterior de la tornilleria
nacional: manda sobre el base en las referencias que traen los dos, porque sus cantidades y
costos son mas recientes.
"""
from .lector_excel import partir_producto


def combinar(base, adicional):
    """Devuelve (filas, resumen). Las filas tienen la forma de lector_excel.leer()."""
    filas = [dict(f) for f in base]
    por_codigo = {partir_producto(f["producto"])[0]: i for i, f in enumerate(filas)}

    actualizadas = nuevas = 0
    for fila in adicional:
        codigo = partir_producto(fila["producto"])[0]
        i = por_codigo.get(codigo)
        if i is None:
            por_codigo[codigo] = len(filas)
            filas.append(dict(fila))
            nuevas += 1
        else:
            filas[i] = dict(fila)
            actualizadas += 1

    resumen = {
        "total": len(filas),
        "actualizadas": actualizadas,
        "nuevas": nuevas,
        "solo_base": len(filas) - actualizadas - nuevas,
    }
    return filas, resumen
