"""Pruebas del mapeo de imágenes de referencia por línea y grupo."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build_catalogo
from lib import imagenes

MAPA = {
    "por_grupo": {"tuercas|Seguridad con nylon": "/img/productos/fey-122-1.jpeg"},
    "por_linea": {"tuercas": "/img/productos/fey-110-1.jpeg"},
}


def _escribir(tmp_path, datos):
    ruta = tmp_path / "imagenes.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return ruta


def _fila(codigo, linea, sublinea, descripcion, tipo="TORNILLERIA"):
    return {
        "_fila": 0, "bodega": "Principal", "tipo": tipo, "linea": linea, "sublinea": sublinea,
        "producto": f"{codigo} | {linea} | {descripcion}", "unidad": "UN",
        "cantidad": 40, "total": 4000, "promedio": 100.0,
    }


# Fila real del Excel: cae en tuercas > "Seguridad con nylon".
TUERCA_NYLON = _fila("7631", "TUERCAS", "Tuerca de seguridad nylon", "TUERCA DE SEG NYLON M3")


def test_el_grupo_manda_sobre_la_linea():
    assert imagenes.para(MAPA, "tuercas", "Seguridad con nylon") == "/img/productos/fey-122-1.jpeg"


def test_un_grupo_sin_mapear_cae_en_la_linea():
    assert imagenes.para(MAPA, "tuercas", "Tuerca mariposa") == "/img/productos/fey-110-1.jpeg"


def test_una_linea_sin_mapear_no_devuelve_imagen():
    assert imagenes.para(MAPA, "arandelas", "Plana") is None


def test_un_mapa_vacio_no_devuelve_imagen():
    assert imagenes.para(imagenes.cargar(""), "tuercas", "Seguridad con nylon") is None
    assert imagenes.para(None, "tuercas", "Seguridad con nylon") is None


def test_un_archivo_inexistente_no_rompe_la_carga(tmp_path):
    assert imagenes.cargar(tmp_path / "no-existe.json") == {"por_grupo": {}, "por_linea": {}}


def test_se_carga_el_mapa_curado_del_disco(tmp_path):
    assert imagenes.cargar(_escribir(tmp_path, MAPA)) == MAPA


def test_el_producto_lleva_la_imagen_en_el_publico_y_en_el_interno():
    publicos, internos, incidencias = build_catalogo.construir([TUERCA_NYLON], 10, 0, MAPA)
    assert publicos[0]["imagen"] == "/img/productos/fey-122-1.jpeg"
    assert internos[0]["imagen"] == "/img/productos/fey-122-1.jpeg"
    assert not incidencias["grupos_sin_imagen"]


def test_sin_mapa_la_imagen_queda_en_nulo_y_se_reporta_el_grupo():
    publicos, _, incidencias = build_catalogo.construir([TUERCA_NYLON], 10, 0, None)
    assert publicos[0]["imagen"] is None
    assert incidencias["grupos_sin_imagen"]["tuercas|Seguridad con nylon"] == 1


def test_el_mapa_curado_apunta_a_imagenes_que_existen():
    """Un archivo renombrado en public/img/productos dejaría fichas con la imagen rota."""
    raiz = Path(__file__).resolve().parent.parent.parent
    mapa = imagenes.cargar(raiz / "data" / "imagenes.json")
    rutas = list(mapa["por_grupo"].values()) + list(mapa["por_linea"].values())
    assert rutas, "el mapeo curado no debería quedar vacío"
    faltan = [r for r in rutas if not (raiz / "public" / r.lstrip("/")).exists()]
    assert not faltan, f"imágenes mapeadas que no existen: {faltan}"
