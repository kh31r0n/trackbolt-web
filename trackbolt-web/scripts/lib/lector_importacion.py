"""Lectura de la lista de importación (hoja hecha a mano, no reporte del ERP).

Formato: cabecera `DESCRIPCION DEL PRODUCTO | CANT | PRECIO UNIT | TOTAL`, filas de título de
sección (solo la columna A, o con la cabecera repetida en B-D) y filas de producto con el código
pegado a la descripción: `11562 WASA 6MM REX`. Se usan la cantidad y `PRECIO UNIT`, que es el
precio mayorista (no el costo del ERP). `TOTAL` es cantidad × precio y no se lee.
"""
import re

import openpyxl

from .lector_excel import FormatoInesperado

CABECERA_ESPERADA = ["DESCRIPCION DEL PRODUCTO", "CANT", "PRECIO UNIT", "TOTAL"]

_ITEM = re.compile(r"^\s*(\d+)\s+(\S.*)$")


def _vacia(celda):
    return celda is None or str(celda).strip() == ""


def clasificar_fila(a, b, c, d):
    """Devuelve None (vacía), ('seccion', titulo), ('item', dict) o ('ignorada', celdas)."""
    if all(_vacia(x) for x in (a, b, c, d)):
        return None
    if isinstance(a, str) and not re.match(r"^\s*\d", a):
        return "seccion", a.strip()
    m = _ITEM.match(str(a)) if a is not None else None
    if m and isinstance(b, (int, float)):
        precio = c if isinstance(c, (int, float)) else None
        return "item", {"codigo": m.group(1), "descripcion": m.group(2).strip(),
                        "cantidad": b, "precio": precio}
    return "ignorada", (a, b, c, d)


def leer(path):
    """Devuelve (items, ignoradas). Falla si la cabecera no es la esperada."""
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb.active
    filas = ws.iter_rows(values_only=True)

    n = 0
    for fila in filas:
        n += 1
        if fila is not None and not all(_vacia(c) for c in fila):
            break
    else:
        raise FormatoInesperado("El archivo está vacío.")

    cabecera = [str(c).strip() if c is not None else "" for c in fila]
    if cabecera[:len(CABECERA_ESPERADA)] != CABECERA_ESPERADA:
        raise FormatoInesperado(
            "La cabecera de la lista de importación no es la esperada.\n"
            f"  esperada: {CABECERA_ESPERADA}\n"
            f"  recibida: {cabecera}"
        )

    items, ignoradas = [], []
    seccion = None
    for fila in filas:
        n += 1
        celdas = tuple(fila[:4]) + (None,) * (4 - len(fila[:4]))
        resultado = clasificar_fila(*celdas)
        if resultado is None:
            continue
        clase, valor = resultado
        if clase == "seccion":
            seccion = valor
        elif clase == "item":
            items.append({"_fila": n, "seccion": seccion, **valor})
        else:
            ignoradas.append({"_fila": n, "contenido": [str(c) if c is not None else None for c in valor]})
    wb.close()
    return items, ignoradas
