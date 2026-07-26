"""Transforma el reporte de existencias REX en un catalogo HTML para Trackbolt."""
import openpyxl
from pathlib import Path
from collections import defaultdict
import json

SRC = "existencias_2026_07_25_22_00_23.xlsx"
OUT = "catalogo_rex.html"
EMAIL_OUT = "correo_catalogo_rex.html"

MULTIPLICADORES = {
    "mostrador": 2.5,
    "usuario_final": 2.0,
    "almacen": 1.75,
    "mayorista": 1.5,
}


def cargar_productos(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    productos = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        _bodega, _tipo, linea, sublinea, producto, unidad, cantidad, _total, promedio = row
        codigo, _linea_dup, descripcion = [p.strip() for p in producto.split("|")]
        valor = round(cantidad * promedio, 2)
        precios = {
            nombre: round(promedio * multiplicador, 2)
            for nombre, multiplicador in MULTIPLICADORES.items()
        }
        productos.append({
            "codigo": codigo,
            "descripcion": descripcion,
            "categoria": linea.strip(),
            "sublinea": sublinea.strip(),
            "unidad": unidad,
            "cantidad": cantidad,
            "promedio": promedio,
            "valor": valor,
            "precios": precios,
            "link": f"https://trackbolt.rex.example/producto/{codigo}",
        })
    productos.sort(key=lambda p: (p["categoria"], p["descripcion"]))
    return productos


def moneda(v):
    return "$" + f"{v:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def agrupar_por_categoria(productos):
    grupos = defaultdict(list)
    for p in productos:
        grupos[p["categoria"]].append(p)
    return dict(sorted(grupos.items()))


def generar_html(productos, out_path):
    categorias = sorted({p["categoria"] for p in productos})
    sublineas = sorted({p["sublinea"] for p in productos})
    grupos = agrupar_por_categoria(productos)

    secciones_html = []
    for categoria, items in grupos.items():
        filas = []
        for p in items:
            filas.append(f"""
            <tr class="producto" data-categoria="{p['categoria']}" data-sublinea="{p['sublinea']}"
                data-buscar="{p['codigo'].lower()} {p['descripcion'].lower()}">
              <td>{p['codigo']}</td>
              <td>{p['descripcion']}</td>
              <td>{p['sublinea']}</td>
              <td>{p['unidad']}</td>
              <td class="num">{p['cantidad']:,}</td>
              <td class="num">{moneda(p['promedio'])}</td>
              <td class="num">{moneda(p['valor'])}</td>
              <td class="num">{moneda(p['precios']['mostrador'])}</td>
              <td class="num">{moneda(p['precios']['usuario_final'])}</td>
              <td class="num">{moneda(p['precios']['almacen'])}</td>
              <td class="num">{moneda(p['precios']['mayorista'])}</td>
              <td><a href="{p['link']}" target="_blank" rel="noopener">Ver detalle</a></td>
            </tr>""")
        secciones_html.append(f"""
        <section class="categoria-grupo" data-categoria="{categoria}">
          <h2>{categoria} <span class="conteo">({len(items)})</span></h2>
          <table>
            <thead>
              <tr>
                <th>Codigo</th><th>Descripcion</th><th>Sublinea</th><th>Unidad</th>
                <th>Cantidad</th><th>Promedio</th><th>Valor</th>
                <th>Mostrador</th><th>Usuario final</th><th>Almacen</th><th>Mayorista</th>
                <th>Detalle</th>
              </tr>
            </thead>
            <tbody>{''.join(filas)}</tbody>
          </table>
        </section>""")

    opciones_categoria = "".join(f'<option value="{c}">{c}</option>' for c in categorias)
    opciones_sublinea = "".join(f'<option value="{s}">{s}</option>' for s in sublineas)

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trackbolt - Catalogo REX</title>
<style>
  :root {{
    --bg: #f7f8fa; --fg: #1a1d23; --card: #ffffff; --border: #e2e5ea;
    --accent: #d62828; --muted: #6b7280;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #14161a; --fg: #e8eaed; --card: #1e2126; --border: #2c3038; --muted: #9aa0aa; }}
  }}
  :root[data-theme="dark"] {{ --bg: #14161a; --fg: #e8eaed; --card: #1e2126; --border: #2c3038; --muted: #9aa0aa; }}
  :root[data-theme="light"] {{ --bg: #f7f8fa; --fg: #1a1d23; --card: #ffffff; --border: #e2e5ea; --muted: #6b7280; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg); color: var(--fg);
  }}
  header {{
    padding: 1.5rem 2rem; background: var(--accent); color: white;
  }}
  header h1 {{ margin: 0; font-size: 1.6rem; }}
  header p {{ margin: 0.25rem 0 0; opacity: 0.9; font-size: 0.9rem; }}
  .filtros {{
    display: flex; flex-wrap: wrap; gap: 0.75rem; padding: 1rem 2rem;
    background: var(--card); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 10;
  }}
  .filtros input, .filtros select {{
    padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--border);
    background: var(--bg); color: var(--fg); font-size: 0.9rem;
  }}
  .filtros input[type="text"] {{ flex: 1; min-width: 200px; }}
  main {{ padding: 1rem 2rem 3rem; max-width: 1200px; margin: 0 auto; }}
  .categoria-grupo {{ margin-bottom: 2rem; }}
  .categoria-grupo h2 {{ font-size: 1.1rem; border-bottom: 2px solid var(--accent); padding-bottom: 0.4rem; }}
  .conteo {{ color: var(--muted); font-weight: normal; font-size: 0.9rem; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card); overflow-x: auto; display: block; }}
  thead, tbody {{ display: table; width: 100%; table-layout: fixed; }}
  th, td {{ padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--border); text-align: left; font-size: 0.85rem; }}
  th {{ color: var(--muted); font-weight: 600; }}
  td.num {{ text-align: right; }}
  tr.producto:hover {{ background: rgba(214, 40, 40, 0.06); }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .oculto {{ display: none !important; }}
  .sin-resultados {{ padding: 2rem; text-align: center; color: var(--muted); }}
</style>
</head>
<body>
<header>
  <h1>Trackbolt</h1>
  <p>Catalogo de inventario &mdash; REX</p>
</header>
<div class="filtros">
  <input type="text" id="buscar" placeholder="Buscar por codigo o descripcion...">
  <select id="filtroCategoria">
    <option value="">Todas las categorias</option>
    {opciones_categoria}
  </select>
  <select id="filtroSublinea">
    <option value="">Todas las sublineas</option>
    {opciones_sublinea}
  </select>
</div>
<main id="catalogo">
  {''.join(secciones_html)}
  <p class="sin-resultados oculto" id="sinResultados">No se encontraron productos.</p>
</main>
<script>
  const buscar = document.getElementById('buscar');
  const filtroCategoria = document.getElementById('filtroCategoria');
  const filtroSublinea = document.getElementById('filtroSublinea');
  const sinResultados = document.getElementById('sinResultados');

  function aplicarFiltros() {{
    const texto = buscar.value.trim().toLowerCase();
    const cat = filtroCategoria.value;
    const sub = filtroSublinea.value;
    let visibles = 0;

    document.querySelectorAll('.categoria-grupo').forEach(grupo => {{
      let filasVisiblesEnGrupo = 0;
      grupo.querySelectorAll('tr.producto').forEach(fila => {{
        const coincideTexto = !texto || fila.dataset.buscar.includes(texto);
        const coincideCat = !cat || fila.dataset.categoria === cat;
        const coincideSub = !sub || fila.dataset.sublinea === sub;
        const mostrar = coincideTexto && coincideCat && coincideSub;
        fila.classList.toggle('oculto', !mostrar);
        if (mostrar) {{ filasVisiblesEnGrupo++; visibles++; }}
      }});
      grupo.classList.toggle('oculto', filasVisiblesEnGrupo === 0);
    }});
    sinResultados.classList.toggle('oculto', visibles !== 0);
  }}

  buscar.addEventListener('input', aplicarFiltros);
  filtroCategoria.addEventListener('change', aplicarFiltros);
  filtroSublinea.addEventListener('change', aplicarFiltros);
</script>
</body>
</html>
"""
    Path(out_path).write_text(html, encoding="utf-8")


MAX_EMAIL_BYTES = 500 * 1024


def construir_email_html(productos, nota=None):
    """Construye el HTML del correo para la lista de productos dada."""
    grupos = agrupar_por_categoria(productos)

    secciones_html = []
    for categoria, items in grupos.items():
        filas = []
        for p in items:
            filas.append(f"""
              <tr>
                <td style="padding:8px 10px;border-bottom:1px solid #e2e5ea;font-size:13px;">{p['codigo']}</td>
                <td style="padding:8px 10px;border-bottom:1px solid #e2e5ea;font-size:13px;">{p['descripcion']}</td>
                <td style="padding:8px 10px;border-bottom:1px solid #e2e5ea;font-size:13px;">{p['sublinea']}</td>
                <td style="padding:8px 10px;border-bottom:1px solid #e2e5ea;font-size:13px;">{p['unidad']}</td>
                <td style="padding:8px 10px;border-bottom:1px solid #e2e5ea;font-size:13px;text-align:right;">{p['cantidad']:,}</td>
                <td style="padding:8px 10px;border-bottom:1px solid #e2e5ea;font-size:13px;text-align:right;font-weight:bold;">{moneda(p['precios']['usuario_final'])}</td>
                <td style="padding:8px 10px;border-bottom:1px solid #e2e5ea;font-size:13px;">
                  <a href="{p['link']}" style="color:#d62828;text-decoration:none;">Ver detalle</a>
                </td>
              </tr>""")
        secciones_html.append(f"""
        <tr>
          <td style="padding:20px 0 8px;">
            <h2 style="margin:0;font-size:16px;color:#1a1d23;border-bottom:2px solid #d62828;padding-bottom:6px;">
              {categoria} <span style="color:#6b7280;font-weight:normal;font-size:13px;">({len(items)})</span>
            </h2>
          </td>
        </tr>
        <tr>
          <td>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#ffffff;">
              <thead>
                <tr>
                  <th style="text-align:left;padding:8px 10px;font-size:12px;color:#6b7280;border-bottom:1px solid #e2e5ea;">Codigo</th>
                  <th style="text-align:left;padding:8px 10px;font-size:12px;color:#6b7280;border-bottom:1px solid #e2e5ea;">Descripcion</th>
                  <th style="text-align:left;padding:8px 10px;font-size:12px;color:#6b7280;border-bottom:1px solid #e2e5ea;">Sublinea</th>
                  <th style="text-align:left;padding:8px 10px;font-size:12px;color:#6b7280;border-bottom:1px solid #e2e5ea;">Unidad</th>
                  <th style="text-align:right;padding:8px 10px;font-size:12px;color:#6b7280;border-bottom:1px solid #e2e5ea;">Cantidad</th>
                  <th style="text-align:right;padding:8px 10px;font-size:12px;color:#6b7280;border-bottom:1px solid #e2e5ea;">Precio</th>
                  <th style="text-align:left;padding:8px 10px;font-size:12px;color:#6b7280;border-bottom:1px solid #e2e5ea;">Detalle</th>
                </tr>
              </thead>
              <tbody>{''.join(filas)}</tbody>
            </table>
          </td>
        </tr>""")

    nota_html = ""
    if nota:
        nota_html = f"""
              <p style="margin:0 0 16px;padding:10px 12px;background:#fff4e5;border:1px solid #f0d9a6;border-radius:4px;font-size:13px;color:#6b4c00;">
                {nota}
              </p>"""

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trackbolt - Catalogo de productos REX</title>
</head>
<body style="margin:0;padding:0;background:#f7f8fa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f7f8fa;">
    <tr>
      <td align="center" style="padding:24px 12px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:800px;background:#ffffff;border-radius:8px;overflow:hidden;">
          <tr>
            <td style="background:#d62828;padding:24px 28px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;">Trackbolt</h1>
              <p style="margin:4px 0 0;color:#ffffff;opacity:0.9;font-size:13px;">Catalogo de productos REX</p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 28px 8px;">
              <p style="margin:0 0 12px;font-size:14px;color:#1a1d23;line-height:1.5;">
                Hola,
              </p>
              <p style="margin:0 0 16px;font-size:14px;color:#1a1d23;line-height:1.5;">
                Te compartimos el catalogo actualizado de productos REX disponibles en Trackbolt.
                A continuacion encontraras el detalle de referencias, existencias y precios vigentes.
                Si tienes alguna pregunta o deseas realizar un pedido, no dudes en contactarnos.
              </p>{nota_html}
            </td>
          </tr>
          <tr>
            <td style="padding:0 28px 24px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                {''.join(secciones_html)}
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:20px 28px;background:#f7f8fa;border-top:1px solid #e2e5ea;">
              <p style="margin:0;font-size:12px;color:#6b7280;">
                Trackbolt &mdash; Este correo fue generado automaticamente a partir de nuestro catalogo de existencias.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return html


def generar_email(productos, out_path, max_bytes=MAX_EMAIL_BYTES):
    """Genera la plantilla de correo, recortando productos si es necesario para no superar max_bytes."""
    total = len(productos)
    html = construir_email_html(productos)

    if len(html.encode("utf-8")) <= max_bytes:
        Path(out_path).write_text(html, encoding="utf-8")
        return total, total

    lo, hi = 0, total
    mejor_n = 0
    mejor_html = None
    while lo <= hi:
        n = (lo + hi) // 2
        subset = productos[:n]
        nota = None
        if n < total:
            nota = (
                f"Este correo muestra {n} de {total} productos disponibles para mantener "
                f"un tamano de archivo manejable. Contactanos para recibir el catalogo completo."
            )
        candidato = construir_email_html(subset, nota=nota)
        if len(candidato.encode("utf-8")) <= max_bytes:
            mejor_n = n
            mejor_html = candidato
            lo = n + 1
        else:
            hi = n - 1

    Path(out_path).write_text(mejor_html, encoding="utf-8")
    return mejor_n, total


if __name__ == "__main__":
    productos = cargar_productos(SRC)
    generar_html(productos, OUT)
    print(f"Generados {len(productos)} productos -> {OUT}")
    incluidos, total = generar_email(productos, EMAIL_OUT)
    tamano_kb = Path(EMAIL_OUT).stat().st_size / 1024
    print(f"Plantilla de correo generada -> {EMAIL_OUT} ({incluidos}/{total} productos, {tamano_kb:.1f} KB)")
