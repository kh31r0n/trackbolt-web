"""Cruza la lista de importación con el inventario del ERP.

El inventario define qué referencias existen; la lista solo cruza existencias: aporta la cantidad
y el precio mayorista (`PRECIO UNIT`) de los códigos que menciona, y el ERP sigue aportando
tipo/línea/sublínea, descripción y costo. Los códigos que la lista trae y el inventario no entran
sin costo y heredan tipo/línea/sublínea del código conocido más cercano dentro de su misma
sección. Ante un código repetido en la hoja no se aplica nada: la fila del inventario se conserva
tal cual.
"""
from collections import defaultdict

from .lector_excel import partir_producto


def fusionar(filas_inventario, items):
    """Devuelve (filas, resumen). Las filas tienen la forma de lector_excel.leer() más
    `precio_mayorista` (None cuando la hoja no trae precio o el código está repetido)."""
    filas = [dict(f) for f in filas_inventario]
    por_codigo = {partir_producto(f["producto"])[0]: f for f in filas}

    agrupados = defaultdict(list)
    for it in items:
        agrupados[it["codigo"]].append(it)
    duplicados = {
        cod: [{"fila": it["_fila"], "descripcion": it["descripcion"], "cantidad": it["cantidad"]}
              for it in lista]
        for cod, lista in agrupados.items() if len(lista) > 1
    }
    unicos = [lista[0] for cod, lista in agrupados.items() if len(lista) == 1]

    conocidos_por_seccion = defaultdict(list)
    for it in unicos:
        if it["codigo"] in por_codigo:
            conocidos_por_seccion[it["seccion"]].append(it["codigo"])

    resumen = {
        "actualizados": 0, "sin_cambio": 0, "nuevos": [],
        "duplicados": duplicados,
    }
    for it in unicos:
        base = por_codigo.get(it["codigo"])
        if base is not None:
            if float(base["cantidad"] or 0) != float(it["cantidad"]):
                resumen["actualizados"] += 1
            else:
                resumen["sin_cambio"] += 1
            base["cantidad"] = it["cantidad"]
            base["precio_mayorista"] = it["precio"]
            continue

        vecino = _vecino(it["codigo"], conocidos_por_seccion.get(it["seccion"], []))
        if vecino is not None:
            ref = por_codigo[vecino]
            tipo, linea, sublinea = ref["tipo"], ref["linea"], ref["sublinea"]
        else:
            tipo, linea, sublinea = "IMPORTACION", it["seccion"], it["seccion"]
        filas.append({
            "_fila": it["_fila"],
            "bodega": "Principal",
            "tipo": tipo,
            "linea": linea,
            "sublinea": sublinea,
            "producto": f"{it['codigo']} | {linea} | {it['descripcion']}",
            "unidad": "UN",
            "cantidad": it["cantidad"],
            "total": 0,
            "promedio": 0,
            "precio_mayorista": it["precio"],
        })
        resumen["nuevos"].append({
            "codigo": it["codigo"], "seccion": it["seccion"], "heredado_de": vecino,
            "linea": linea, "sublinea": sublinea,
        })

    # Lo que la lista no menciona conserva la existencia del inventario. En la línea REX eso
    # significa cantidades viejas, así que se reporta aparte.
    importados = set(agrupados)
    resumen["solo_inventario"] = sum(1 for c in por_codigo if c not in importados)
    resumen["rex_sin_cobertura"] = sorted(
        (c for c, f in por_codigo.items()
         if "REX" in str(f["tipo"] or "").upper() and c not in importados),
        key=lambda c: (len(c), c),
    )
    return filas, resumen


def _vecino(codigo, candidatos):
    if not candidatos:
        return None
    return min(candidatos, key=lambda c: (abs(int(c) - int(codigo)), int(c)))
