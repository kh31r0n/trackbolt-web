"""Pruebas de la combinación de los dos reportes de existencias del ERP."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import inventario


def _fila(codigo, linea, sublinea, descripcion, cantidad, promedio, tipo="TORNILLERIA"):
    return {
        "_fila": 0, "bodega": "Principal", "tipo": tipo, "linea": linea, "sublinea": sublinea,
        "producto": f"{codigo} | {linea} | {descripcion}", "unidad": "UN",
        "cantidad": cantidad, "total": cantidad * promedio, "promedio": promedio,
    }


# Filas reales: 8125 y 3056 están en los dos reportes con cantidades distintas; 1249 solo en el
# reporte de septiembre; 11562 solo en el de julio, que es el único que trae la línea REX.
BASE = [
    _fila("8125", "ARANDELAS", "Arandela especial bicro", "ARAN PLANA ESPECIAL 5/16 / 8MM", 3854, 36.53),
    _fila("3056", "TORNILOS BRISTOL", "Tornillo bristol con cabeza milimetrico negro", "TOR BRISTOL CON CAB MM 12.9 12 X 40", 27, 2628.17),
    _fila("11562", "ARANDELAS REX", "ARANDELA PLANA REX", "ARANDELA PLANA 6MM REX", 970, 14.1, tipo="TORNILLOS REX"),
]
ADICIONAL = [
    _fila("8125", "ARANDELAS", "Arandela especial bicro", "ARAN PLANA ESPECIAL 5/16 / 8MM", 3854, 36.53),
    _fila("3056", "TORNILOS BRISTOL", "Tornillo bristol con cabeza milimetrico negro", "TOR BRISTOL CON CAB MM 12.9 12 X 40", 7, 2628.15),
    _fila("1249", "TORNILLOS CABEZA HEXAGONAL", "Tornillo hexagonal grado 5 negro", "TOR HEX G5 UNC NEGRO 1/4 X 2.1/2", 50, 119.97),
]


def _por_codigo(filas):
    return {f["producto"].split(" | ")[0]: f for f in filas}


def test_el_reporte_posterior_manda_en_cantidad_y_costo():
    filas, resumen = inventario.combinar(BASE, ADICIONAL)
    fila = _por_codigo(filas)["3056"]
    assert fila["cantidad"] == 7 and fila["promedio"] == 2628.15
    assert resumen["actualizadas"] == 2


def test_las_referencias_que_solo_trae_el_posterior_se_agregan():
    filas, resumen = inventario.combinar(BASE, ADICIONAL)
    assert _por_codigo(filas)["1249"]["cantidad"] == 50
    assert resumen["nuevas"] == 1


def test_lo_que_el_posterior_no_menciona_se_conserva():
    """El reporte de existencias adicionales no trae la línea REX."""
    filas, resumen = inventario.combinar(BASE, ADICIONAL)
    rex = _por_codigo(filas)["11562"]
    assert rex["cantidad"] == 970 and rex["tipo"] == "TORNILLOS REX"
    assert resumen == {"total": 4, "actualizadas": 2, "nuevas": 1, "solo_base": 1}


def test_no_muta_las_entradas():
    inventario.combinar(BASE, ADICIONAL)
    assert BASE[1]["cantidad"] == 27 and BASE[1]["promedio"] == 2628.17


def test_sin_reporte_adicional_no_cambia_nada():
    filas, resumen = inventario.combinar(BASE, [])
    assert [f["producto"] for f in filas] == [f["producto"] for f in BASE]
    assert resumen == {"total": 3, "actualizadas": 0, "nuevas": 0, "solo_base": 3}
