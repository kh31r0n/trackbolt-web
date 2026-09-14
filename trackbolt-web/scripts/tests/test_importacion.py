"""Pruebas de la lista de importación y su fusión con el ERP, con filas reales de la hoja."""
import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import fusion, lector_importacion
from lib.lector_excel import FormatoInesperado


# --- Clasificación de filas ----------------------------------------------------

def test_fila_vacia():
    assert lector_importacion.clasificar_fila(None, None, None, None) is None


def test_seccion_sola():
    assert lector_importacion.clasificar_fila("WASAS DE PRESION", None, None, None) == ("seccion", "WASAS DE PRESION")


def test_seccion_con_cabecera_repetida():
    clase, titulo = lector_importacion.clasificar_fila("PERNOS DE RUEDA ", "CANT", "PRECIO UNIT", "TOTAL")
    assert (clase, titulo) == ("seccion", "PERNOS DE RUEDA")


def test_item():
    clase, item = lector_importacion.clasificar_fila("11562 WASA 6MM REX", 970.0, 21.15, 20515.5)
    assert clase == "item"
    assert item == {"codigo": "11562", "descripcion": "WASA 6MM REX", "cantidad": 970.0, "precio": 21.15}


def test_item_sin_precio_sigue_siendo_item():
    clase, item = lector_importacion.clasificar_fila("11562 WASA 6MM REX", 970.0, None, None)
    assert clase == "item"
    assert item["cantidad"] == 970.0 and item["precio"] is None


def test_item_sin_cantidad_se_ignora():
    """Fila 476 de la hoja: código y descripción sin cantidad ni precio."""
    clase, _ = lector_importacion.clasificar_fila("2980 TORNILLO HEX MM CL10.9 ROSCA TOTAL  12 X 1.75 X 40", None, None, None)
    assert clase == "ignorada"


def test_cantidad_sin_descripcion_se_ignora():
    clase, _ = lector_importacion.clasificar_fila(None, 358.0, 701.0, 250958.0)
    assert clase == "ignorada"


def test_gran_total_se_ignora():
    clase, _ = lector_importacion.clasificar_fila(None, None, None, 556738700.39)
    assert clase == "ignorada"


# --- Lectura del Excel ----------------------------------------------------------

def _hoja(tmp_path, filas):
    wb = openpyxl.Workbook()
    for fila in filas:
        wb.active.append(fila)
    ruta = tmp_path / "importacion.xlsx"
    wb.save(ruta)
    return ruta


def test_leer_asigna_seccion_y_fila(tmp_path):
    ruta = _hoja(tmp_path, [
        [None, None, None, None],
        ["DESCRIPCION DEL PRODUCTO", "CANT", "PRECIO UNIT", "TOTAL"],
        ["WASAS DE PRESION"],
        ["11562 WASA 6MM REX", 970, 21.15, 20515.5],
        ["PERNOS DE RUEDA ", "CANT", "PRECIO UNIT", "TOTAL"],
        ["11195 PERNO DE RUEDA CL10.9 18 X 1.50 X 80 LO TRAS", 145, 2571.84, 372916.8],
        [None, 358, 701, 250958],
    ])
    items, ignoradas = lector_importacion.leer(ruta)
    assert [(i["_fila"], i["seccion"], i["codigo"], i["cantidad"], i["precio"]) for i in items] == [
        (4, "WASAS DE PRESION", "11562", 970, 21.15),
        (6, "PERNOS DE RUEDA", "11195", 145, 2571.84),
    ]
    assert [i["_fila"] for i in ignoradas] == [7]


def test_leer_rechaza_cabecera_distinta(tmp_path):
    ruta = _hoja(tmp_path, [["Código", "Descripción", "CANTIDAD"], ["88533", "X", 3]])
    with pytest.raises(FormatoInesperado):
        lector_importacion.leer(ruta)


# --- Fusión con el ERP -----------------------------------------------------------

def _fila_erp(codigo, linea, sublinea, descripcion, cantidad, promedio, tipo="TORNILLERIA"):
    return {
        "_fila": 0, "bodega": "Principal", "tipo": tipo, "linea": linea, "sublinea": sublinea,
        "producto": f"{codigo} | {linea} | {descripcion}", "unidad": "UN",
        "cantidad": cantidad, "total": cantidad * promedio, "promedio": promedio,
    }


def _item(fila, seccion, codigo, descripcion, cantidad, precio=None):
    return {"_fila": fila, "seccion": seccion, "codigo": codigo, "descripcion": descripcion,
            "cantidad": cantidad, "precio": precio}


def _codigos(filas):
    return [f["producto"].split(" | ")[0] for f in filas]


SEC = "TORNILLO HEXAGONAL MILIMETRICO 10.9"
ERP = [
    _fila_erp("3092", "TORNILLOS CABEZA HEXAGONAL", "Tornillo hexagonal milimetrico 10.9", "TOR HEX MM 10.9 PASO 2.00 16 X 220", 44, 2920.76),
    _fila_erp("3126", "TORNILLOS CABEZA HEXAGONAL", "Tornillo hexagonal milimetrico 10.9", "TOR HEX MM 10.9 PASO 2.50 18 X 35", 100, 1500),
    _fila_erp("10912", "TORNILLO HEXAGONAL REX", "TORNILLO HEXAGONAL MM 10,9 REX", "TORNILLO HEX MM CL10.9 RP 24 X 3.00 X 80", 49, 3052.56, tipo="TORNILLOS REX"),
    _fila_erp("11564", "ARANDELAS REX", "ARANDELA PLANA REX", "ARANDELA PLANA 16MM REX", 1400, 126.9, tipo="TORNILLOS REX"),
    _fila_erp("8960", "MANUAL", "BROCAS", "BROCA PARA METAL ACERO RAPIDO 1/8", 30, 2500, tipo="HERRAMIENTA"),
]


def test_coincidente_toma_cantidad_y_precio_mayorista_de_la_lista():
    """Fila 9 de la hoja: 11564 WASA 16MM REX, 470 unidades a $190,35."""
    filas, resumen = fusion.fusionar(ERP, [_item(9, "WASAS DE PRESION", "11564", "WASA 16MM REX", 470.0, 190.35)])
    fila = next(f for f in filas if f["producto"].startswith("11564"))
    assert fila["cantidad"] == 470.0
    assert fila["precio_mayorista"] == 190.35
    assert fila["promedio"] == 126.9   # el costo sigue siendo el del ERP
    assert fila["producto"] == "11564 | ARANDELAS REX | ARANDELA PLANA 16MM REX"
    assert resumen["actualizados"] == 1 and resumen["sin_cambio"] == 0
    assert ERP[3]["cantidad"] == 1400 and "precio_mayorista" not in ERP[3]  # la entrada no se muta


def test_no_retira_lo_que_la_lista_no_menciona():
    """El inventario manda: la lista solo cruza existencias, no recorta el catálogo."""
    filas, resumen = fusion.fusionar(ERP, [_item(9, "WASAS DE PRESION", "11564", "WASA 16MM REX", 470)])
    assert _codigos(filas) == ["3092", "3126", "10912", "11564", "8960"]
    assert [f["cantidad"] for f in filas] == [44, 100, 49, 470, 30]
    assert resumen["solo_inventario"] == 4
    # Las REX que la lista no menciona conservan la cantidad vieja; se reportan aparte.
    assert resumen["rex_sin_cobertura"] == ["10912"]


def test_lista_vacia_deja_el_inventario_igual():
    filas, resumen = fusion.fusionar(ERP, [])
    assert [f["cantidad"] for f in filas] == [f["cantidad"] for f in ERP]
    assert resumen["solo_inventario"] == 5


def test_misma_cantidad_cuenta_como_sin_cambio():
    _, resumen = fusion.fusionar(ERP, [_item(9, "WASAS DE PRESION", "11564", "WASA 16MM REX", 1400)])
    assert resumen["actualizados"] == 0 and resumen["sin_cambio"] == 1


def test_nuevo_hereda_del_vecino_mas_cercano_de_su_seccion():
    items = [
        _item(557, SEC, "3092", "TORNILLO HEX MM CL10.9 ROSCA PARCIAL 16 X 2.00 X 220", 44),
        _item(571, SEC, "3125", "TORNILLO HEX MM CL10.9 ROSCA TOTAL 18 X 2.50 X 30", 85),
        _item(572, SEC, "3126", "TORNILLO HEX MM CL10.9 ROSCA TOTAL 18 X 2.50 X 35", 100),
        _item(676, SEC, "10912", "TORNILLO HEX MM CL10.9 ROSCA PARCIAL 24 X 3.00 X 80", 7),
    ]
    filas, resumen = fusion.fusionar(ERP, items)
    assert _codigos(filas) == ["3092", "3126", "10912", "11564", "8960", "3125"]
    nueva = filas[-1]
    assert nueva["tipo"] == "TORNILLERIA"
    assert nueva["linea"] == "TORNILLOS CABEZA HEXAGONAL"
    assert nueva["sublinea"] == "Tornillo hexagonal milimetrico 10.9"
    assert nueva["producto"] == "3125 | TORNILLOS CABEZA HEXAGONAL | TORNILLO HEX MM CL10.9 ROSCA TOTAL 18 X 2.50 X 30"
    assert nueva["cantidad"] == 85 and nueva["promedio"] == 0 and nueva["unidad"] == "UN"
    assert nueva["precio_mayorista"] is None
    assert nueva["_fila"] == 571
    assert resumen["nuevos"] == [{
        "codigo": "3125", "seccion": SEC, "heredado_de": "3126",
        "linea": "TORNILLOS CABEZA HEXAGONAL", "sublinea": "Tornillo hexagonal milimetrico 10.9",
    }]


def test_nuevo_no_hereda_de_otra_seccion():
    items = [
        _item(9, "WASAS DE PRESION", "11564", "WASA 16MM REX", 470),
        _item(571, SEC, "3125", "TORNILLO HEX MM CL10.9 ROSCA TOTAL 18 X 2.50 X 30", 85),
    ]
    filas, resumen = fusion.fusionar(ERP, items)
    nueva = filas[-1]
    assert nueva["tipo"] == "IMPORTACION"
    assert nueva["linea"] == SEC and nueva["sublinea"] == SEC
    assert resumen["nuevos"][0]["heredado_de"] is None


def test_codigo_repetido_no_se_aplica_y_se_reporta():
    items = [
        _item(557, SEC, "3092", "TORNILLO HEX MM CL10.9 ROSCA PARCIAL 16 X 2.00 X 220", 44),
        _item(558, SEC, "3092", "TORNILLO HEX MM CL10.9 ROSCA PARCIAL 16 X 2.00 X 230", 81),
    ]
    filas, resumen = fusion.fusionar(ERP, items)
    # La fila del inventario se conserva tal cual: cantidad de julio y sin precio de la lista.
    assert len(filas) == len(ERP)
    assert filas[0]["cantidad"] == 44 and "precio_mayorista" not in filas[0]
    assert resumen["duplicados"] == {"3092": [
        {"fila": 557, "descripcion": "TORNILLO HEX MM CL10.9 ROSCA PARCIAL 16 X 2.00 X 220", "cantidad": 44},
        {"fila": 558, "descripcion": "TORNILLO HEX MM CL10.9 ROSCA PARCIAL 16 X 2.00 X 230", "cantidad": 81},
    ]}
    assert resumen["actualizados"] == 0


def test_repetido_no_sirve_de_vecino():
    items = [
        _item(557, SEC, "3092", "A", 44),
        _item(558, SEC, "3092", "B", 81),
        _item(560, SEC, "3093", "TORNILLO HEX MM CL10.9 ROSCA PARCIAL 16 X 2.00 X 240", 10),
        _item(572, SEC, "3126", "TORNILLO HEX MM CL10.9 ROSCA TOTAL 18 X 2.50 X 35", 100),
    ]
    _, resumen = fusion.fusionar(ERP, items)
    assert resumen["nuevos"][0]["heredado_de"] == "3126"
