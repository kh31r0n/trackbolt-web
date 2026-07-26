# Trackbolt

Sitio web y catálogo de **Trackbolt**, distribuidor de tornillería de alta resistencia para
maquinaria pesada (Bogotá, Colombia). Reemplaza la tienda Shopify de trackbolt.co por un sitio
estático en Astro cuyo catálogo se genera con Python desde el reporte de existencias del ERP.

> *Hechos para aguantar. Hechos para avanzar.*

---

## Estado

Funcionando y verificado.

| | |
|---|---|
| Referencias en catálogo | **2.790** |
| Líneas de producto | **11** |
| Páginas estáticas generadas | **2.811** (una por referencia + contenido) |
| Tiempo de build | ~7 s |
| JavaScript enviado al navegador | 4 KB · CSS 15 KB · índice de búsqueda 46 KB con gzip |
| Pruebas | 82 (pytest) |

Pendiente de revisión visual en navegador y de los insumos de marca listados más abajo.

---

## Arranque rápido

```bash
# Entorno de Python (una sola vez)
python3 -m venv .venv
.venv/bin/pip install -r trackbolt-web/scripts/requirements.txt

# Dependencias del sitio (una sola vez)
cd trackbolt-web && npm install

# Generar el catálogo y levantar el sitio
make catalogo        # Excel -> JSON
make dev             # http://localhost:4321
```

`make todo` corre catálogo, pruebas y build. El manual completo de operación está en
[`trackbolt-web/README.md`](trackbolt-web/README.md).

---

## Cómo funciona

```
inventario … .xlsx          reporte de existencias del ERP (fuente de verdad)
        │
        │   scripts/build_catalogo.py        ← Python: limpia, clasifica, extrae especificaciones
        ▼
data/generado/*.json        catálogo público · catálogo interno · líneas · reporte
public/datos/*.json         índices que descarga el navegador
        │
        │   astro build                      ← 2.811 páginas estáticas
        ▼
dist/                       se publica en cualquier hosting estático
```

El ERP entrega una sola hoja plana donde todo el dato técnico —diámetro, largo, paso, grado,
acabado, número de parte del fabricante— viene enterrado en texto libre dentro de la descripción.
El script de Python existe para convertir eso en campos estructurados y filtrables, y en nombres
que un cliente entienda:

```
TORNILLO HEX MM CL10.9 RP 16 X 2.00 X 120
        ↓
Tornillo hexagonal M16 × 120 mm, clase 10.9, rosca parcial
```

Cobertura sobre las 2.398 referencias de tornillería: diámetro 99 %, sistema 99 %, tipo de cabeza
76 %, largo 74 %, grado 71 %. Lo que el parser no puede afirmar queda vacío en lugar de salir mal.

---

## Decisiones de producto

| Tema | Decisión |
|---|---|
| Precios | El público ve **un solo precio** (costo × 2.0, redondeado a $50 COP). Los cuatro niveles —mostrador, usuario final, almacén, mayorista— solo en `/interno/`. |
| Inventario | El cliente ve **estado sin cantidades**: *Disponible* (≥ 10 unidades), *Pocas unidades* (1–9), *Bajo pedido*. Las cantidades exactas solo en `/interno/`. |
| Clasificación | 11 líneas por tipo de pieza, al estilo de boltdepot.com, con filtros por diámetro, largo, grado, material, cabeza y rosca. |
| Línea REX | Se muestra como **sello de calidad**, no como categoría aparte: quien busca «tornillo de zapata» ve las 151 juntas. |
| Alcance | Catálogo navegable y cotización por WhatsApp. **Sin carrito ni pagos en línea.** |
| Vista interna | Publicada sin contraseña por decisión del cliente para esta prueba de concepto. Marcada `noindex` y fuera del sitemap. |

El precio al público y el umbral de disponibilidad son parámetros del generador
(`--multiplo`, `--umbral`), no valores incrustados en el código.

---

## Estructura del repositorio

```
trackbolt-web/                  el proyecto
├─ scripts/                     generador del catálogo (Python) + 82 pruebas
├─ data/                        el Excel del ERP y los JSON generados
├─ src/                         páginas y componentes de Astro
├─ public/                      estáticos e índices que descarga el navegador
├─ Makefile · README.md         comandos y manual de operación
│
CLAUDE.md                       guía de arquitectura para Claude Code
inventario total trackbolt 07-25-26.xlsx    copia original del reporte del ERP
WhatsApp Image *.jpeg           material de marca original (rinoceronte, logo, claims)
```

Los archivos `transform_catalogo.py`, `catalogo_rex.html`, `correo_catalogo_rex.html` y
`existencias_*.xlsx` de la raíz son el **script anterior de un solo uso** y sus salidas. Quedan
como referencia histórica: `trackbolt-web/scripts/` los reemplazó.

---

## Hallazgos en los datos del ERP

El generador los reporta en cada corrida y los deja en `data/generado/reporte.json`. Conviene
corregirlos en el ERP: el catálogo mejora solo.

- **4 referencias con costo promedio negativo** y **1 en cero** → se publican como
  «Precio a confirmar».
- **1 descripción con un `|` extra**, que rompería un `split("|")` ingenuo.
- **21 referencias (0,9 %)** cuya medida no es interpretable desde la descripción.
- Errores de escritura consistentes: `TORNILOS BRISTOL`, `TUERCAS ` con espacio final, `TUERGA`,
  `MERCEDEZ`, `HIUNDAY`, `JHON DEER`, medidas escritas como `1"""`.
- Sublíneas que no corresponden a la descripción (una `VARILLA ROSCADA` clasificada como
  espárrago, por ejemplo). El sitio respeta lo que dice el ERP.

Descubrimiento aprovechado: **63 referencias traen el número de parte del fabricante de maquinaria**
(`6Y0846` de Caterpillar, `20Y3211210` de Komatsu, `4F3648`…). El catálogo permite buscar por ese
número, que es como realmente pide un mecánico de maquinaria pesada.

---

## Pendientes

1. **Logotipo vectorial.** El monograma del encabezado es una reconstrucción
   (`src/components/Logo.astro`, `public/favicon.svg`). Reemplazar por el SVG original.
2. **Proteger `/interno/`** antes de producción: Basic Auth en el hosting o Cloudflare Access.
   La página ya lleva la advertencia.
3. **Tipografía.** Se usa la pila del sistema para no depender de un CDN. Para acercarse al gótico
   condensado de la marca, colocar `Archivo Black` en `public/fuentes/`; la variable `--display`
   ya está lista.
4. **Fotografía.** El sitio funciona sin ella (los iconos de línea son SVG de dibujo técnico).
   Faltan los bodegones por línea, las fotos por sector y la imagen 1200×630 para redes.
5. **Datos de negocio.** Horario de atención y NIT no aparecían en el sitio anterior; agregarlos
   en `src/data/sitio.ts`.

---

## Publicación

Salida estática pura. Sirve en Vercel, Netlify, Cloudflare Pages o nginx.

```bash
cd trackbolt-web && make build     # resultado en dist/
```
