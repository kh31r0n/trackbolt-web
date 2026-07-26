"""Lectura del reporte de existencias del ERP."""
import openpyxl

CABECERA_ESPERADA = [
    "Bodega", "Tipo", "Linea", "Sublinea", "Producto",
    "Unidad medida", "Cantidad", "Total", "Promedio",
]


class FormatoInesperado(Exception):
    pass


def leer(path):
    """Devuelve la lista de filas crudas como diccionarios.

    Falla temprano y con mensaje claro si el ERP cambia el orden de las columnas:
    es preferible eso a publicar un catalogo con los datos corridos de lugar.
    """
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb.active
    filas = ws.iter_rows(values_only=True)

    try:
        cabecera = [str(c).strip() if c is not None else "" for c in next(filas)]
    except StopIteration:
        raise FormatoInesperado("El archivo está vacío.")

    if cabecera[:len(CABECERA_ESPERADA)] != CABECERA_ESPERADA:
        raise FormatoInesperado(
            "La cabecera del Excel no es la esperada.\n"
            f"  esperada: {CABECERA_ESPERADA}\n"
            f"  recibida: {cabecera}"
        )

    salida = []
    for n, fila in enumerate(filas, start=2):
        if fila is None or all(c is None or str(c).strip() == "" for c in fila):
            continue
        salida.append({
            "_fila": n,
            "bodega": fila[0],
            "tipo": fila[1],
            "linea": fila[2],
            "sublinea": fila[3],
            "producto": fila[4],
            "unidad": fila[5],
            "cantidad": fila[6],
            "total": fila[7],
            "promedio": fila[8],
        })
    wb.close()
    return salida


def partir_producto(producto):
    """'8960 | MANUAL | BROCA 1/8' -> ('8960', 'MANUAL', 'BROCA 1/8').

    Usa maxsplit=2 porque hay descripciones que contienen el separador '|'.
    """
    partes = str(producto).split("|", 2)
    while len(partes) < 3:
        partes.append("")
    return tuple(p.strip() for p in partes)
