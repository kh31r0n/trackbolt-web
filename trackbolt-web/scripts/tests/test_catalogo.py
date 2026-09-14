"""Pruebas del generador de catalogo, con casos reales del Excel del ERP.

    /home/jjimenez/trackbolt/.venv/bin/python -m pytest scripts/tests -q
"""
import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build_catalogo
from lib import especificaciones as E
from lib import lector_excel, normalizar, precios, taxonomia


# --- Lectura del Excel -------------------------------------------------------

def test_partir_producto_normal():
    assert lector_excel.partir_producto("8960 | MANUAL | BROCA 1/8") == ("8960", "MANUAL", "BROCA 1/8")


def test_partir_producto_con_pipe_extra():
    """Hay una fila del Excel cuya descripcion contiene el separador."""
    codigo, linea, desc = lector_excel.partir_producto("100 | TUERCAS | TUERCA A | B ESPECIAL")
    assert codigo == "100"
    assert linea == "TUERCAS"
    assert desc == "TUERCA A | B ESPECIAL"


def _excel(tmp_path, filas, nombre="reporte.xlsx"):
    wb = openpyxl.Workbook()
    for fila in filas:
        wb.active.append(fila)
    ruta = tmp_path / nombre
    wb.save(ruta)
    return ruta


FILA_ERP = ["Principal", "TORNILLERIA", "ARANDELAS", "Arandela especial bicro",
            "8125 | ARANDELAS | ARAN PLANA ESPECIAL 5/16 / 8MM", "UN", 3854, 140794.31, 36.53]


def test_lee_las_columnas_por_nombre(tmp_path):
    """'EXISTENCIAS PRODUCTOS ADICIONALES' intercala 'Ubicacion' antes de 'Producto'."""
    sin = _excel(tmp_path, [
        ["Bodega", "Tipo", "Linea", "Sublinea", "Producto", "Unidad medida", "Cantidad", "Total", "Promedio"],
        FILA_ERP,
    ], "sin.xlsx")
    con = _excel(tmp_path, [
        ["Bodega", "Tipo", "Linea", "Sublinea", "Ubicacion", "Producto", "Unidad medida", "Cantidad", "Total", "Promedio"],
        FILA_ERP[:4] + [None] + FILA_ERP[4:],
    ], "con.xlsx")
    assert lector_excel.leer(sin) == lector_excel.leer(con)
    assert lector_excel.leer(con)[0]["cantidad"] == 3854


def test_falla_si_falta_una_columna(tmp_path):
    ruta = _excel(tmp_path, [
        ["Bodega", "Tipo", "Linea", "Sublinea", "Producto", "Unidad medida", "Cantidad", "Total"],
        FILA_ERP[:8],
    ])
    with pytest.raises(lector_excel.FormatoInesperado, match="Promedio"):
        lector_excel.leer(ruta)


# --- Fracciones en pulgadas --------------------------------------------------

@pytest.mark.parametrize("texto,esperado", [
    ("3/8", 0.375),
    ("1.1/2", 1.5),
    ("1-1/4", 1.25),
    ("21/2", 2.5),          # '2.1/2' mal escrito en el ERP
    ("1.15/16", 1.9375),
    ("15/16", 0.9375),
    ("2,9/16", 2.5625),     # coma decimal
    ("1", 1.0),
])
def test_valor_pulgadas(texto, esperado):
    assert E.valor_pulgadas(texto) == pytest.approx(esperado)


def test_formato_pulgadas():
    assert E.formato_pulgadas("1.1/2") == '1-1/2"'
    assert E.formato_pulgadas("21/2") == '2-1/2"'
    assert E.formato_pulgadas("3/8") == '3/8"'


# --- Medidas metricas --------------------------------------------------------

@pytest.mark.parametrize("desc,medida,paso", [
    ("TORNILLO HEX MM CL10.9 RP 16 X 2.00 X 120", "M16 × 120 mm", "2 mm"),
    ("TOR HEX MM 10.9 PASO 2.00 16 X 270", "M16 × 270 mm", "2 mm"),
    ("TOR HEX MM 10.9 PASO FINO 1.50 22 X 200", "M22 × 200 mm", "1.5 mm"),
    ("TORNILLO ZAPATA 12.9 20 X 60 PASO 1.5 6Y0846", "M20 × 60 mm", "1.5 mm"),
    ("TOR ZAPATA 12.9 24X120 PASO 2", "M24 × 120 mm", "2 mm"),
    ("PERNO FORD M14X1,50X70 10.9", "M14 × 70 mm", "1.5 mm"),
    ("TORNILLO HEX MM CL8.8 RT 14 - 2.00 X 40", "M14 × 40 mm", "2 mm"),
    ("TOR CAB CILIN PHILLIPS T. JISS 5-0.80 X 12", "M5 × 12 mm", "0.8 mm"),
    ("ESPARRAGO MILIMETRICO 8 1.25X1.25 X 70", "M8 × 70 mm", "1.25 mm"),
    ("TUERCA DE SEG FLANGE STOVER PASO 1.50 M20", "M20", "1.5 mm"),
    ("TUERCA DE SEG NYLON MM PASO 3.00 24", "M24", "3 mm"),
    ("TUERCA HEXAGONAL CL 8 MM 16 PASO 2.0", "M16", "2 mm"),
    ("TUERCA HEX ALTA M12 X 1.50", "M12", "1.5 mm"),
    ("TUERCA HEX INOX M 14", "M14", None),
    ("TUERCA HEX FLANGE BICRO 8M P 1.25", "M8", "1.25 mm"),
])
def test_medidas_metricas(desc, medida, paso):
    esp = E.extraer(desc)
    assert esp["sistema"] == "metrico"
    assert esp["medida"] == medida
    assert esp["paso"] == paso


@pytest.mark.parametrize("desc,medida", [
    ("TOR HEX G 8 UNC NEGRO 3/8 X 1.1/2", '3/8" × 1-1/2"'),
    ("TOR HEX G 8 UNC NEGRO 1.1/2 X 12", '1-1/2" × 12"'),
    ("TORNILLO ZAPATA 12.9 5/8 X 2,1/4 9G3110", '5/8" × 2-1/4"'),
    ("TOR CUCHILLA 12.9 1 -1/4X 4", '1-1/4" × 4"'),
    ("TUERCA DE SEG NYLON UNF 3/16", '3/16"'),
    ("TUERCA HEX GRA 5 UNC 5/16", '5/16"'),
    ("WASA DE PRESION INOX 304 5/32", '5/32"'),
    ("ARAN PLANA MOGOLLA IRIZ X UND 3/4 X 2 1/2", '3/4" × 2-1/2"'),
    ("ESPARRAGO MIXTO 1/2 X 1/2 X 3", '1/2" × 3"'),
])
def test_medidas_pulgadas(desc, medida):
    esp = E.extraer(desc)
    assert esp["sistema"] == "pulgadas"
    assert esp["medida"] == medida


def test_no_confunde_modelo_de_vehiculo_con_fraccion():
    """'250/350' y '416/420' son modelos, no fracciones en pulgadas."""
    assert E.extraer("PERNO FORD 250/350 14X2,00X66 10.9")["medida"] == "M14 × 66 mm"
    assert E.extraer("PERNO CAT 416/420 20 X 70 ESTRIA 23")["medida"] == "M20 × 70 mm"


def test_descarta_medida_implausible():
    """'22 X 5' no es un tornillo de 5 mm: el largo no puede ser tan menor que el diametro."""
    esp = E.extraer('PERNO INTER 22 X 5 ESTRIA ESTRIA 1" (MULA)')
    assert esp["largo"] is None


def test_prisionero_corto_si_es_valido():
    assert E.extraer("TOR BRISTOL SIN CAB MM 10.9 5 X 5")["medida"] == "M5 × 5 mm"


def test_arandela_sin_rosca_no_lleva_m():
    """En arandelas el diametro no designa una rosca."""
    assert E.extraer("ARANDELA CONICA DE 18", roscado=False)["diametro"] == "18 mm"
    assert E.extraer("ARANDELA CONICA DE 18", roscado=True)["diametro"] == "M18"


# --- Grado, acabado, cabeza, rosca ------------------------------------------

@pytest.mark.parametrize("desc,grado", [
    ("TORNILLO HEX MM CL10.9 RP 14 X 2.00 X 90", "Clase 10.9"),
    ("TOR HEX MM 8.8 PASO 1.00 8 X 80", "Clase 8.8"),
    ("TOR ZAPATA 12.9 1/2 X 2", "Clase 12.9"),
    ("TORNILLO ZAPATA FLANGE 13.9 5/8 X 2", "Clase 13.9"),
    ("TOR HEX G 8 UNC NEGRO 5/16 X 1", "Grado 8"),
    ("TUERCA HEX GRA 5 UNC 7/16", "Grado 5"),
    ("TORNILLO HEXAGONAL GR8 RT UNC 1/4 X 3/4", "Grado 8"),
    ("TUERCA HEX UNC INOX 304 UNC 1/2", "Inoxidable A2 (304)"),
    ("ESPARRAGO B7 3/4 X 5", "ASTM A193 B7"),
    ("TUERCA HEX BICRO CLASE 6 M-4 PASO 070", "Clase 6"),
])
def test_grado(desc, grado):
    assert E.extraer(desc)["grado"] == grado


@pytest.mark.parametrize("desc,acabado", [
    ("ARAN PLANA ZINCADA POR UNIDAD 1/2", "Zincado"),
    ("WASA DE PRESION NEGRA 3/8", "Negro"),
    ("TUERCA HEX FLANGE BICRO 8M P 1.25", "Bicromatado"),
    ("TOR BRISTOL CAB AVELLAN INOX 1/4 X 5/8", "Inoxidable"),
    ("TORNILLO HEX MM CL10.9 RP 16 X 2.00 X 120", "Negro"),   # implicito por la clase
])
def test_acabado(desc, acabado):
    assert E.extraer(desc)["acabado"] == acabado


def test_cabeza_y_rosca():
    esp = E.extraer("TORNILLO HEX FLANGE MM CL10.9 RP 16 X 2.00 X 35")
    assert esp["cabeza"] == "Flange (con arandela integrada)"
    assert esp["rosca_largo"] == "Parcial"
    esp = E.extraer("TORNILLO HEX MM CL10.9 RI 10 X 1.50 X 40")
    assert esp["rosca_largo"] == "Total"
    esp = E.extraer("TORNILLO HEX MM CL10.9 ROSCA PARCIAL 18 X 2.50 X 65")   # lista de importación
    assert esp["rosca_largo"] == "Parcial"
    assert esp["medida"] == "M18 × 65 mm"
    assert esp["paso"] == "2.5 mm"
    esp = E.extraer("TOR BRISTOL SIN CAB UNC G8 3/16 X 1/2")
    assert esp["cabeza"] == "Sin cabeza (prisionero)"
    assert esp["rosca_serie"] == "UNC (ordinaria)"


# --- Numero de parte OEM -----------------------------------------------------

@pytest.mark.parametrize("desc,parte", [
    ("TORNILLO ZAPATA 12.9 20 X 60 PASO 1.5 6Y0846", "6Y0846"),
    ("TORNILLO CUCHILLA CL12.9 1/2 X 1.3/4 4F3648", "4F3648"),
    ("PERNO CARGADOR 1V3323 3/4X2.3/8 G.8", "1V3323"),
    ("TORNILLO ZAPATA FLANGE 13.9 20 X 55 PASO 1.5 20Y3211210", "20Y3211210"),
])
def test_numero_de_parte(desc, parte):
    assert E.extraer(desc)["numero_parte"] == parte


def test_numero_de_parte_no_se_lee_como_medida():
    esp = E.extraer("TORNILLO ZAPATA 12.9 5/8 X 2,1/4 9G3110")
    assert esp["medida"] == '5/8" × 2-1/4"'
    assert esp["numero_parte"] == "9G3110"


# --- Nombres comerciales -----------------------------------------------------

def test_nombre_comercial():
    esp = E.extraer("TORNILLO HEX MM CL10.9 RP 16 X 2.00 X 120")
    base = normalizar.base_comercial("Tornillo hexagonal milimetrico 10.9")
    assert base == "Tornillo hexagonal"
    assert E.nombre_comercial(base, esp) == "Tornillo hexagonal M16 × 120 mm, clase 10.9, rosca parcial"


def test_base_comercial_quita_lo_que_ya_es_especificacion():
    assert normalizar.base_comercial("Tornillo hexagonal grado 8 negro") == "Tornillo hexagonal"
    assert normalizar.base_comercial("Wasa negra") == "Arandela de presión"
    assert normalizar.base_comercial("Tornillo hexagonal flange 8.8 / 10.9") == "Tornillo hexagonal flange"


def test_limpieza_de_comillas_del_erp():
    assert normalizar.limpiar('ARAN PLANA ZINCADA POR UNIDAD 1"""') == 'ARAN PLANA ZINCADA POR UNIDAD 1"'
    assert normalizar.limpiar("Broca SDS 5/8 X 12''") == 'Broca SDS 5/8 X 12"'


# --- Taxonomia ---------------------------------------------------------------

@pytest.mark.parametrize("tipo,linea,sublinea,desc,esperado", [
    ("HERRAMIENTA", "MANUAL", "Brocas", "BROCA 1/8", "herramienta"),
    ("TORNILLERIA", "TORNILLOS CABEZA HEXAGONAL", "Tornillo hexagonal milimetrico 10.9",
     "TOR HEX MM 10.9 16 X 270", "tornillos-hexagonales"),
    ("TORNILLERIA", "TORNILLOS CABEZA HEXAGONAL", "Tornillo hexagonal zapata",
     "TOR ZAPATA 12.9 20X55", "rodaje-zapata-cuchilla"),
    ("TORNILLOS REX", "TORNILLO ZAPATA REX", "TORNILLO PARA ZAPATA REX",
     "TORNILLO ZAPATA 12.9 20 X 60", "rodaje-zapata-cuchilla"),
    ("TORNILLERIA", "TORNILLOS CARRIAGE", "Tornillo cuchilla",
     "TOR CUCHILLA 12.9 1/2 X 2.1/2", "rodaje-zapata-cuchilla"),
    ("TORNILLOS REX", "TORNILLO FLANGE REX", "TORNILLO HEXAGONAL FLANGE 10,9 REX",
     "TORNILLO HEX FLANGE", "tornillos-flange"),
    ("TORNILLERIA", "TUERCAS ", "Tuerca flange ", "TUERCA HEX FLANGE", "tuercas"),
    ("TORNILLOS REX", "TUERCAS REX", "TUERCA CUADRADA ZAPATA REX", "TUERCA CUADRADA ZTA", "tuercas"),
    ("TORNILLERIA", "WASAS", "Wasa negra", "WASA DE PRESION NEGRA 3/8", "arandelas"),
    ("TORNILLERIA", "TORNILOS BRISTOL", "Tornillo bristol con cabeza negro", "TOR BRISTOL", "tornillos-bristol"),
    ("TORNILLERIA", "PERNOS", "Pernos", "PERNO FORD", "pernos-rueda"),
    ("TORNILLERIA", "ESPARRAGOS / VARILLAS", "Esparrago b7", "ESPARRAGO B7", "esparragos-varillas"),
    ("TORNILLERIA", "PINES", "Pin chaveta ", "PINES CHAVETAS", "pines-remaches"),
    ("TORNILLERIA", "TORNILLOS CABEZA CENTRAL", "Central", "TORNILLO CENTRAL", "tornillos-especiales"),
])
def test_clasificar(tipo, linea, sublinea, desc, esperado):
    assert taxonomia.clasificar(tipo, linea, sublinea, desc) == esperado


def test_una_tuerca_flange_no_cae_en_la_linea_flange():
    """El orden de las reglas importa: primero tuercas, luego flange."""
    assert taxonomia.clasificar("TORNILLOS REX", "TUERCAS REX", "TUERCA FLANGE REX",
                                "TUERCA FLANGE") == "tuercas"


def test_toda_linea_tiene_metadatos():
    for slug in {taxonomia.clasificar(t, l, s, "") for t, l, s in
                 [("HERRAMIENTA", "MANUAL", "Brocas"), ("TORNILLERIA", "PERNOS", "Pernos")]}:
        assert slug in taxonomia.LINEAS_POR_SLUG


# --- Lineas que no se publican -----------------------------------------------

@pytest.mark.parametrize("tipo,linea", [
    ("TORNILLERIA", "PERNOS"),
    ("TORNILLERIA", "ESPARRAGOS / VARILLAS"),
    ("TORNILLERIA", "ESPARRAGOS  / VARILLAS"),     # el ERP repite espacios
    ("TORNILLERIA", "TORNILLOS CARRIAGE"),
    ("TORNILLERIA", "TORNILLOS CABEZA CENTRAL"),
    ("TORNILLERIA", "TORNILLOS ESTUFA "),
    ("TORNILLERIA", "TORNILLOS LAMINA"),
    ("TORNILLERIA", "PINES"),
    ("TORNILLERIA", "REMACHES"),
    ("TORNILLERIA", "CHAZOS"),
    ("HERRAMIENTA", "MANUAL"),
    ("HERRAMIENTA", "ELECTRICA"),                  # cualquier herramienta futura
])
def test_linea_excluida(tipo, linea):
    assert taxonomia.excluida(tipo, linea) is True


@pytest.mark.parametrize("tipo,linea", [
    ("TORNILLOS REX", "PERNOS DE RUEDA REX"),      # los de rueda importados se quedan
    ("TORNILLOS REX", "TORNILLO CARIAJE REX"),
    ("TORNILLERIA", "TORNILLOS CABEZA HEXAGONAL"),
    ("TORNILLERIA", "TUERCAS "),
    ("TORNILLERIA", "WASAS"),
    ("TORNILLERIA", "ARANDELAS"),
])
def test_linea_publicada(tipo, linea):
    assert taxonomia.excluida(tipo, linea) is False


# --- Precios -----------------------------------------------------------------

def test_precios_sin_redondeo_por_defecto():
    """11562 ARANDELA PLANA 6MM: costo 14,1; a $50 el mayorista (21,15) quedaba en 0."""
    niveles = precios.calcular(14.1)
    assert niveles == {"mostrador": 35.25, "usuario_final": 28.2, "almacen": 24.68, "mayorista": 21.15}


def test_precios_redondean_a_50_si_se_pide():
    niveles = precios.calcular(1018.66, multiplo=50)
    assert niveles["usuario_final"] == 2050     # 1018.66 x 2.0 = 2037.32 -> 2050
    assert niveles["mayorista"] == 1550
    assert niveles["mostrador"] == 2550


def test_mayorista_de_la_lista_deriva_los_niveles():
    """11494 TORNILLO AVELLAN BRISTOL: costo ERP 193,64 pero la lista fija el mayorista en $352."""
    niveles = precios.calcular(193.64, mayorista=352)
    assert niveles == {"mostrador": 586.67, "usuario_final": 469.33, "almacen": 410.67, "mayorista": 352}
    # Códigos nuevos: sin costo en el ERP, pero con precio en la lista.
    assert precios.calcular(0, mayorista=352)["mayorista"] == 352
    # Sin precio en la lista se vuelve al costo del ERP.
    assert precios.calcular(14.1, mayorista=None)["mayorista"] == 21.15


def test_costo_no_valido_no_genera_precio():
    """4 referencias del Excel traen costo negativo y 1 en cero."""
    assert precios.calcular(-42167.32) == {}
    assert precios.calcular(0) == {}
    assert precios.calcular(0, mayorista=0) == {}


# --- Reparto público / interno -----------------------------------------------

def test_lo_publico_no_lleva_costo_cantidad_ni_precio():
    """Lo que baja el navegador (productos.json, buscador.json) no puede filtrar costos ni precios."""
    fila = {
        "_fila": 2, "bodega": "Principal", "tipo": "TORNILLOS REX", "linea": "ARANDELAS REX",
        "sublinea": "ARANDELA PLANA REX", "producto": "11562 | ARANDELAS REX | ARANDELA PLANA 6MM REX",
        "unidad": "UN", "cantidad": 970, "total": 13677, "promedio": 14.1, "precio_mayorista": 21.15,
    }
    publicos, internos, _ = build_catalogo.construir([fila], umbral=10, multiplo=0)
    assert not {"costo", "cantidad", "valor_inventario", "precios", "precio"} & set(publicos[0])
    assert "p" not in build_catalogo.construir_buscador(publicos)[0]
    assert internos[0]["costo"] == 14.1 and internos[0]["cantidad"] == 970
    assert internos[0]["precios"] == {"mostrador": 35.25, "usuario_final": 28.2, "almacen": 24.68, "mayorista": 21.15}


def test_moneda_cop():
    assert normalizar.moneda_cop(2037.32) == "$2.037"
    assert normalizar.moneda_cop(1250000) == "$1.250.000"
    assert normalizar.moneda_cop(None) == "A confirmar"
