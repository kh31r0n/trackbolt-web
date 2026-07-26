#!/usr/bin/env python3
"""Genera el catalogo de Trackbolt a partir del reporte de existencias del ERP.

    python scripts/build_catalogo.py

Salidas en data/generado/:
    productos.json          publico  (sin costo ni cantidad; lo usa el build de Astro)
    productos-interno.json  interno  (costo, cantidad, valor y los 4 niveles de precio)
    lineas.json             arbol de lineas, grupos, facetas y conteos
    buscador.json           indice compacto que se descarga en el navegador
    reporte.json            trazabilidad e incidencias de datos del Excel
"""
import argparse
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import especificaciones as esp_mod
from lib import lector_excel, normalizar, precios, salidas, taxonomia

RAIZ = Path(__file__).resolve().parent.parent
EXCEL = RAIZ / "data" / "inventario total trackbolt 07-25-26.xlsx"
DESTINO = RAIZ / "data" / "generado"

ESTADOS = {
    2: {"clave": "disponible", "texto": "Disponible", "detalle": "En bodega, despacho inmediato"},
    1: {"clave": "pocas", "texto": "Pocas unidades", "detalle": "Existencia limitada, confirma antes de pedir"},
    0: {"clave": "pedido", "texto": "Bajo pedido", "detalle": "Se consigue por importación o fabricación"},
}


def estado_de(cantidad, umbral):
    if cantidad is None or cantidad <= 0:
        return 0
    return 2 if cantidad >= umbral else 1


def construir(filas, umbral, multiplo):
    publicos, internos = [], []
    incidencias = {
        "costo_negativo": [], "costo_cero": [], "sin_medida": [],
        "sublineas_no_mapeadas": Counter(), "pipes_extra": [],
    }

    for fila in filas:
        codigo, linea_dup, descripcion_erp = lector_excel.partir_producto(fila["producto"])
        if str(fila["producto"]).count("|") > 2:
            incidencias["pipes_extra"].append(codigo)

        tipo = normalizar.limpiar(fila["tipo"])
        linea_erp = normalizar.limpiar(fila["linea"])
        sublinea_erp = normalizar.limpiar(fila["sublinea"])
        descripcion_erp = normalizar.limpiar(descripcion_erp)
        unidad = normalizar.limpiar(fila["unidad"]) or "UN"

        cantidad = float(fila["cantidad"] or 0)
        costo = float(fila["promedio"] or 0)

        linea_slug = taxonomia.clasificar(tipo, linea_erp, sublinea_erp, descripcion_erp)
        if linea_slug == "otros":
            incidencias["sublineas_no_mapeadas"][f"{tipo} > {linea_erp} > {sublinea_erp}"] += 1

        es_herramienta = linea_slug == "herramienta"
        # En arandelas y pines el diametro no designa una rosca: se muestra '20 mm', no 'M20'.
        roscado = linea_slug not in {"arandelas", "pines-remaches"}
        grupo = taxonomia.grupo(sublinea_erp, normalizar.titulo)
        especs = esp_mod.extraer(descripcion_erp, sublinea_erp, es_herramienta, roscado)

        if es_herramienta:
            nombre = normalizar.titulo(descripcion_erp)
            marca = grupo
        else:
            base = normalizar.base_comercial(sublinea_erp)
            nombre = esp_mod.nombre_comercial(base, especs)
            marca = "REX" if "REX" in linea_erp.upper() else None
            if not especs.get("medida"):
                incidencias["sin_medida"].append(codigo)

        precio_publico, niveles = precios.calcular(costo, multiplo)
        if costo < 0:
            incidencias["costo_negativo"].append({"codigo": codigo, "costo": costo})
        elif costo == 0:
            incidencias["costo_cero"].append(codigo)

        nivel = estado_de(cantidad, umbral)
        es_rex = "REX" in linea_erp.upper() or "REX" in sublinea_erp.upper()

        comun = {
            "codigo": codigo,
            "nombre": nombre,
            "linea": linea_slug,
            "linea_nombre": taxonomia.LINEAS_POR_SLUG[linea_slug]["nombre"],
            "grupo": grupo,
            "descripcion_erp": descripcion_erp,
            "unidad": unidad,
            "marca": marca,
            "es_rex": es_rex,
            "numero_parte": especs["numero_parte"],
            "referencia_fabricante": especs["referencia_fabricante"],
            "especificaciones": {
                "sistema": especs["sistema"],
                "medida": especs["medida"],
                "diametro": especs["diametro"],
                "largo": especs["largo"],
                "paso": especs["paso"],
                "grado": especs["grado"],
                "acabado": especs["acabado"],
                "cabeza": especs["cabeza"],
                "rosca_serie": especs["rosca_serie"],
                "rosca_largo": especs["rosca_largo"],
                "vehiculo": especs["vehiculo"],
            },
            "orden_diametro": especs["diametro_orden"] or 0,
            "orden_largo": especs["largo_orden"] or 0,
        }

        publicos.append({
            **comun,
            "precio": precio_publico,
            "estado": nivel,
            "estado_texto": ESTADOS[nivel]["texto"],
            "estado_clave": ESTADOS[nivel]["clave"],
            "estado_detalle": ESTADOS[nivel]["detalle"],
        })

        internos.append({
            **comun,
            "linea_erp": linea_erp,
            "sublinea_erp": sublinea_erp,
            "cantidad": int(cantidad) if cantidad == int(cantidad) else cantidad,
            "costo": round(costo, 2),
            "valor_inventario": round(cantidad * costo, 2),
            "precios": niveles,
            "estado_clave": ESTADOS[nivel]["clave"],
        })

    orden = {l["slug"]: i for i, l in enumerate(taxonomia.LINEAS)}
    clave = lambda p: (orden[p["linea"]], p["grupo"], p["orden_diametro"], p["orden_largo"], p["nombre"])
    publicos.sort(key=clave)
    internos.sort(key=clave)
    return publicos, internos, incidencias


def _facetas(items):
    """Cuenta valores por faceta, descartando los nulos."""
    campos = {
        "grado": lambda p: p["especificaciones"]["grado"],
        "acabado": lambda p: p["especificaciones"]["acabado"],
        "sistema": lambda p: p["especificaciones"]["sistema"],
        "diametro": lambda p: p["especificaciones"]["diametro"],
        "cabeza": lambda p: p["especificaciones"]["cabeza"],
        "rosca_largo": lambda p: p["especificaciones"]["rosca_largo"],
        "vehiculo": lambda p: p["especificaciones"]["vehiculo"],
        "estado": lambda p: p["estado_texto"],
    }
    salida = {}
    for nombre, obtener in campos.items():
        cuenta = Counter(v for v in (obtener(p) for p in items) if v)
        if not cuenta:
            continue
        if nombre == "diametro":
            # Ordena por medida real, no alfabeticamente: M8 antes que M10.
            por_valor = {}
            for p in items:
                d = p["especificaciones"]["diametro"]
                if d:
                    por_valor[d] = p["orden_diametro"]
            valores = sorted(cuenta.items(), key=lambda kv: por_valor.get(kv[0], 0))
        else:
            valores = sorted(cuenta.items(), key=lambda kv: (-kv[1], kv[0]))
        salida[nombre] = [{"valor": v, "total": n} for v, n in valores]
    return salida


def construir_lineas(publicos):
    por_linea = defaultdict(list)
    for p in publicos:
        por_linea[p["linea"]].append(p)

    lineas = []
    for meta in taxonomia.LINEAS:
        items = por_linea.get(meta["slug"], [])
        if not items:
            continue
        grupos = Counter(p["grupo"] for p in items)
        lineas.append({
            **meta,
            "total": len(items),
            "grupos": [{"nombre": g, "slug": normalizar.slug(g), "total": n}
                       for g, n in sorted(grupos.items(), key=lambda kv: (-kv[1], kv[0]))],
            "facetas": _facetas(items),
        })
    return lineas


def construir_buscador(publicos):
    """Indice compacto para filtrar en el navegador. Claves cortas a proposito."""
    productos = []
    for p in publicos:
        e = p["especificaciones"]
        productos.append({
            "c": p["codigo"],
            "n": p["nombre"],
            "l": p["linea"],
            "g": p["grupo"],
            "p": p["precio"],
            "e": p["estado"],
            "s": e["sistema"] or "",
            "d": e["diametro"] or "",
            "r": e["grado"] or "",
            "a": e["acabado"] or "",
            "h": e["cabeza"] or "",
            "t": e["rosca_largo"] or "",
            "v": e["vehiculo"] or "",
            "k": p["numero_parte"] or p["referencia_fabricante"] or "",
            "x": p["orden_diametro"],
            "y": p["orden_largo"],
            "q": 1 if p["es_rex"] else 0,
        })
    return productos


def construir_interno_web(internos):
    """Indice de la vista interna: cantidad, costo, valor y los cuatro niveles."""
    filas = []
    for p in internos:
        filas.append({
            "c": p["codigo"],
            "n": p["nombre"],
            "l": p["linea_nombre"],
            "s": p["sublinea_erp"],
            "u": p["unidad"],
            "q": p["cantidad"],
            "k": p["costo"],
            "v": p["valor_inventario"],
            "m": p["precios"].get("mostrador"),
            "f": p["precios"].get("usuario_final"),
            "a": p["precios"].get("almacen"),
            "y": p["precios"].get("mayorista"),
        })
    return filas


def main():
    ap = argparse.ArgumentParser(description="Genera el catalogo de Trackbolt desde el Excel del ERP.")
    ap.add_argument("--excel", default=str(EXCEL), help="ruta del reporte de existencias")
    ap.add_argument("--salida", default=str(DESTINO), help="carpeta de salida de los JSON")
    ap.add_argument("--umbral", type=int, default=10,
                    help="unidades desde las que un producto se muestra como Disponible (def. 10)")
    ap.add_argument("--multiplo", type=int, default=50,
                    help="multiplo de redondeo de precios en COP (def. 50)")
    args = ap.parse_args()

    ruta_excel = Path(args.excel)
    if not ruta_excel.exists():
        sys.exit(f"No existe el archivo: {ruta_excel}")

    print(f"Leyendo {ruta_excel.name} ...")
    filas = lector_excel.leer(ruta_excel)
    print(f"  {len(filas)} filas leídas")

    publicos, internos, incidencias = construir(filas, args.umbral, args.multiplo)
    lineas = construir_lineas(publicos)
    buscador = construir_buscador(publicos)

    valor_total = sum(i["valor_inventario"] for i in internos)
    reporte = {
        "generado_en": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "archivo": ruta_excel.name,
        "total_referencias": len(publicos),
        "umbral_disponible": args.umbral,
        "multiplicadores": precios.MULTIPLICADORES,
        "nivel_publico": precios.NIVEL_PUBLICO,
        "valor_inventario": round(valor_total, 2),
        "por_linea": {l["slug"]: l["total"] for l in lineas},
        "por_estado": {ESTADOS[k]["clave"]: v for k, v in
                       sorted(Counter(p["estado"] for p in publicos).items(), reverse=True)},
        "incidencias": {
            "costo_negativo": incidencias["costo_negativo"],
            "costo_cero": incidencias["costo_cero"],
            "referencias_con_pipe_extra": incidencias["pipes_extra"],
            "sin_medida_reconocida": {
                "total": len(incidencias["sin_medida"]),
                "codigos": incidencias["sin_medida"][:40],
            },
            "sublineas_no_mapeadas": dict(incidencias["sublineas_no_mapeadas"]),
        },
    }

    destino = Path(args.salida)
    # public/ lo sirve Astro tal cual: ahi van los indices que descarga el navegador.
    web = RAIZ / "public" / "datos"
    archivos = [
        salidas.escribir(destino, "productos.json", publicos),
        salidas.escribir(destino, "productos-interno.json", internos),
        salidas.escribir(destino, "lineas.json", lineas),
        salidas.escribir(destino, "reporte.json", reporte),
        salidas.escribir(web, "buscador.json", buscador, compacto=True),
        salidas.escribir(web, "interno.json", construir_interno_web(internos), compacto=True),
    ]

    print("\nLíneas de producto:")
    for l in lineas:
        print(f"  {l['total']:>5}  {l['nombre']}")
    print(f"\nEstado de inventario: " + ", ".join(
        f"{v} {k}" for k, v in reporte["por_estado"].items()))
    print(f"Valor de inventario: {normalizar.moneda_cop(valor_total)} COP")

    sin_medida = reporte["incidencias"]["sin_medida_reconocida"]["total"]
    no_tornilleria = sum(1 for p in publicos if p["linea"] == "herramienta")
    print(f"\nIncidencias del Excel (ver reporte.json):")
    print(f"  costo negativo: {len(incidencias['costo_negativo'])}"
          f" | costo en cero: {len(incidencias['costo_cero'])}"
          f" | descripción con '|' extra: {len(incidencias['pipes_extra'])}")
    print(f"  sin medida reconocida: {sin_medida} de {len(publicos) - no_tornilleria} referencias de tornillería")
    if incidencias["sublineas_no_mapeadas"]:
        print(f"  sublíneas sin línea asignada: {len(incidencias['sublineas_no_mapeadas'])}")
        for k, v in incidencias["sublineas_no_mapeadas"].items():
            print(f"     {v:>4}  {k}")

    print("\nArchivos generados:")
    for ruta, tam in archivos:
        print(f"  {ruta.name:<24} {salidas.kb(tam):>8}")


if __name__ == "__main__":
    main()
