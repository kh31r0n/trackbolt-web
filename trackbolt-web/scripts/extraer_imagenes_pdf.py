#!/usr/bin/env python3
"""Extrae los dibujos tecnicos del catalogo PDF del fabricante y arma la hoja de contactos.

Es una herramienta de un solo uso: no forma parte de `make catalogo`. El PDF viene impreso desde
Word ("Microsoft: Print To PDF") y mezcla, en las mismas paginas, el cromo de la maqueta (pestañas
de navegacion, cabeceras, logos) con los dibujos de producto. El cromo se repite pagina tras
pagina, asi que se descarta por md5 duplicado; lo que queda y tiene tamaño de dibujo se guarda.

Los codigos del catalogo son del fabricante y no coinciden con los del ERP de Trackbolt: por eso
aqui solo se extraen imagenes y su contexto (pagina, numero de item, titulo de la familia), y el
cruce con el catalogo se hace a mano en data/imagenes.json.
"""

import argparse
import hashlib
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pymupdf

RAIZ = Path(__file__).resolve().parent.parent
PDF = "../inventario/catalogs/124-catalago-de-produtos-fey.pdf"
DESTINO_IMG = "public/img/productos"
DESTINO_DATOS = "data/generado"
PREFIJO = "fey"

# Pestañas de navegacion y rotulos de la maqueta: nunca son el titulo de la familia.
NAVEGACION = {
    "PORCAS",
    "CONEXÕES HIDRÁULICAS",
    "CONEXÕES E ACESSÓRIOS",
    "PARAFUSOS",
    "TRATOR",
    "AGRÍCOLA",
    "MOTOCICLETA",
    "AUTOMOTIVO",
    "PINOS DE CENTRO",
    "GRAMPOS",
    "ÍNDICE",
    "NOTAS",
}

ITEM = re.compile(r"^(\d{3})\.\s*(.*)$")

# Un dibujo mide del orden de 130x140 px; los iconos de la maqueta no llegan a 100 y las cabeceras
# son franjas larguisimas (1186x294, 1201x72).
LADO_MINIMO = 100
PROPORCION_MAXIMA = 3.0


def _repetidas(doc):
    """Devuelve el md5 de las imagenes que aparecen mas de una vez (el cromo de la maqueta)."""
    cuenta = Counter()
    for pagina in doc:
        for imagen in pagina.get_images(full=True):
            cuenta[_md5(doc, imagen[0])] += 1
    return {firma for firma, n in cuenta.items() if n > 1}


def _md5(doc, xref):
    return hashlib.md5(doc.extract_image(xref)["image"]).hexdigest()


def _lineas(pagina):
    """Devuelve [(texto, y, cuerpo)] de la pagina, en orden de lectura."""
    salida = []
    for bloque in pagina.get_text("dict")["blocks"]:
        for linea in bloque.get("lines", []):
            texto = "".join(t["text"] for t in linea["spans"]).strip()
            if not texto:
                continue
            cuerpo = max(t["size"] for t in linea["spans"])
            salida.append((texto, linea["bbox"][1], cuerpo))
    return salida


def _titulo(lineas):
    """Titulo de la familia: la linea en mayusculas de mayor cuerpo que no sea de la maqueta."""
    candidatas = [
        (cuerpo, texto)
        for texto, _, cuerpo in lineas
        if texto == texto.upper()
        and texto not in NAVEGACION
        and len(texto) > 3
        and not texto[0].isdigit()
    ]
    if not candidatas:
        return ""
    return max(candidatas)[1]


def _items(lineas):
    """Devuelve [(numero, descripcion, y)] de los items ("114. Linha Métrica") de la pagina."""
    salida = []
    for texto, y, _ in lineas:
        m = ITEM.match(texto)
        if m:
            salida.append((m.group(1), m.group(2).strip(), y))
    return salida


def _item_de(items, y):
    """El item al que pertenece un dibujo: el ultimo que empieza por encima; si no, el primero."""
    if not items:
        return None
    previos = [it for it in items if it[2] <= y + 12]
    return (previos[-1] if previos else items[0])[0]


def extraer(doc, destino_img, prefijo=PREFIJO):
    """Escribe los dibujos en destino_img y devuelve el inventario como lista de diccionarios."""
    repetidas = _repetidas(doc)
    destino_img.mkdir(parents=True, exist_ok=True)
    inventario = []
    vistas = set()
    por_item = Counter()
    for numero, pagina in enumerate(doc, start=1):
        lineas = _lineas(pagina)
        items = _items(lineas)
        if not items:
            # Paginas institucionales, indices y tablas de equivalencias: no hay producto que ilustrar.
            continue
        titulo = _titulo(lineas)
        for imagen in pagina.get_images(full=True):
            xref = imagen[0]
            info = doc.extract_image(xref)
            ancho, alto = info["width"], info["height"]
            firma = hashlib.md5(info["image"]).hexdigest()
            if firma in repetidas or firma in vistas:
                continue
            if ancho < LADO_MINIMO or alto < LADO_MINIMO:
                continue
            if max(ancho / alto, alto / ancho) > PROPORCION_MAXIMA:
                continue
            rects = pagina.get_image_rects(xref)
            y = rects[0].y0 if rects else 0
            item = _item_de(items, y)
            por_item[item] += 1
            nombre = f"{prefijo}-{item}-{por_item[item]}.{info['ext']}"
            (destino_img / nombre).write_bytes(info["image"])
            vistas.add(firma)
            inventario.append(
                {
                    "archivo": f"/img/productos/{nombre}",
                    "pagina": numero,
                    "item": item,
                    "titulo": titulo,
                    "ancho": ancho,
                    "alto": alto,
                }
            )
    return inventario


def hoja_de_contactos(inventario, ruta):
    """Escribe una pagina HTML con todos los dibujos, para elegir a ojo el mapeo por grupo."""
    tarjetas = []
    for reg in inventario:
        tarjetas.append(
            "<figure>"
            f'<img src="../../public{html.escape(reg["archivo"])}" loading="lazy" alt="">'
            f'<figcaption><b>{html.escape(reg["item"])}</b> · p. {reg["pagina"]}<br>'
            f'{html.escape(reg["titulo"])}<br><code>{html.escape(reg["archivo"])}</code>'
            "</figcaption></figure>"
        )
    ruta.write_text(
        "<!doctype html><meta charset='utf-8'><title>Dibujos del catálogo</title>"
        "<style>body{font:14px system-ui;margin:2rem;background:#fafafa}"
        "main{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:1rem}"
        "figure{margin:0;padding:.75rem;background:#fff;border:1px solid #ddd;border-radius:6px}"
        "img{max-width:100%;height:auto;display:block;margin:0 auto .5rem}"
        "figcaption{font-size:12px;color:#444;line-height:1.4}code{font-size:11px;color:#888}"
        "</style>"
        f"<h1>{len(inventario)} dibujos extraídos</h1>"
        "<p>Elegí el archivo que corresponde a cada grupo y pegalo en "
        "<code>data/imagenes.json</code>.</p><main>" + "".join(tarjetas) + "</main>",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="Extrae los dibujos de producto de un catálogo PDF")
    parser.add_argument("--pdf", default=PDF, help=f"catálogo PDF (def. {PDF})")
    parser.add_argument("--destino", default=DESTINO_IMG, help=f"carpeta de imágenes (def. {DESTINO_IMG})")
    parser.add_argument("--datos", default=DESTINO_DATOS, help=f"carpeta del inventario (def. {DESTINO_DATOS})")
    parser.add_argument("--prefijo", default=PREFIJO, help=f"prefijo de los archivos (def. {PREFIJO})")
    args = parser.parse_args()

    pdf = Path(args.pdf)
    if not pdf.is_absolute():
        pdf = RAIZ / pdf
    if not pdf.exists():
        sys.exit(f"No existe el archivo: {pdf}")

    destino_img = RAIZ / args.destino
    destino_datos = RAIZ / args.datos
    destino_datos.mkdir(parents=True, exist_ok=True)

    print(f"Leyendo {pdf.name} ...")
    doc = pymupdf.open(pdf)
    print(f"  {doc.page_count} páginas")
    inventario = extraer(doc, destino_img, args.prefijo)
    print(f"  {len(inventario)} dibujos escritos en {args.destino}/")

    json_ruta = destino_datos / f"imagenes-{args.prefijo}.json"
    json_ruta.write_text(
        json.dumps(inventario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    html_ruta = destino_datos / f"imagenes-{args.prefijo}.html"
    hoja_de_contactos(inventario, html_ruta)
    print(f"  {json_ruta.relative_to(RAIZ)}")
    print(f"  {html_ruta.relative_to(RAIZ)}  <- abrilo para curar el mapeo")


if __name__ == "__main__":
    main()
