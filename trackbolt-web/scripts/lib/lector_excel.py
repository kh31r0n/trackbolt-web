"""Lectura de un reporte de existencias del ERP."""
import openpyxl

# Campo de salida -> nombre de la columna en el Excel. Las columnas se buscan por nombre:
# 'EXISTENCIAS PRODUCTOS ADICIONALES' intercala una columna 'Ubicacion' antes de 'Producto',
# y leer por posicion correria todos los campos en silencio.
COLUMNAS = {
    "bodega": "Bodega",
    "tipo": "Tipo",
    "linea": "Linea",
    "sublinea": "Sublinea",
    "producto": "Producto",
    "unidad": "Unidad medida",
    "cantidad": "Cantidad",
    "total": "Total",
    "promedio": "Promedio",
}


class FormatoInesperado(Exception):
    pass


def _indices(cabecera):
    """Posicion de cada campo en la cabecera. Falla si falta alguna columna obligatoria."""
    posicion = {}
    for i, nombre in enumerate(cabecera):
        posicion.setdefault(nombre, i)
    faltan = [col for col in COLUMNAS.values() if col not in posicion]
    if faltan:
        raise FormatoInesperado(
            "La cabecera del Excel no trae todas las columnas esperadas.\n"
            f"  faltan:   {faltan}\n"
            f"  esperada: {list(COLUMNAS.values())}\n"
            f"  recibida: {cabecera}"
        )
    return {campo: posicion[col] for campo, col in COLUMNAS.items()}


def leer(path):
    """Devuelve la lista de filas crudas como diccionarios.

    Falla temprano y con mensaje claro si el ERP renombra o quita una columna: es preferible
    eso a publicar un catalogo con los datos corridos de lugar. Las columnas que sobran
    (p. ej. 'Ubicacion') se ignoran.
    """
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb.active
    filas = ws.iter_rows(values_only=True)

    try:
        cabecera = [str(c).strip() if c is not None else "" for c in next(filas)]
    except StopIteration:
        raise FormatoInesperado("El archivo está vacío.")

    idx = _indices(cabecera)

    salida = []
    for n, fila in enumerate(filas, start=2):
        if fila is None or all(c is None or str(c).strip() == "" for c in fila):
            continue
        valor = lambda campo: fila[idx[campo]] if idx[campo] < len(fila) else None
        salida.append({"_fila": n, **{campo: valor(campo) for campo in COLUMNAS}})
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
