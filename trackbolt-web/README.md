# Trackbolt — sitio web y catálogo

Sitio estático en **Astro** cuyo catálogo se genera con un **script de Python** a partir del
reporte de existencias del ERP. Reemplaza a trackbolt.co.

- **2.790 referencias**, 11 líneas de producto, una página estática por referencia (2.811 páginas).
- **Precio al público** visible (costo × 2.0, redondeado a $50 COP).
- **Disponibilidad sin cantidades** para el cliente; cantidades y costos solo en `/interno/`.
- Cero dependencias de terceros en el navegador: 4 KB de JavaScript y 15 KB de CSS.

---

## Puesta en marcha

```bash
# 1. Entorno de Python (una sola vez)
python3 -m venv ../.venv
../.venv/bin/pip install -r scripts/requirements.txt

# 2. Dependencias del sitio (una sola vez)
npm install

# 3. Generar el catálogo desde el Excel y levantar el sitio
make catalogo
make dev            # http://localhost:4321
```

## Actualizar el catálogo cuando llega un Excel nuevo

1. Copia el reporte de existencias a `data/` (mismo formato de columnas).
2. Ajusta la constante `EXCEL` en `scripts/build_catalogo.py`, o pásalo por parámetro:

```bash
make catalogo
# o bien
../.venv/bin/python scripts/build_catalogo.py --excel "data/inventario 2026-08.xlsx"
```

3. Revisa el resumen que imprime el script (incidencias, sublíneas sin clasificar).
4. `make build` y publica `dist/`.

```bash
make todo      # catalogo + pruebas + build
```

### Parámetros del generador

| Parámetro | Def. | Qué hace |
|---|---|---|
| `--excel` | `data/inventario total trackbolt 07-25-26.xlsx` | Reporte de existencias de entrada |
| `--salida` | `data/generado` | Carpeta de los JSON |
| `--umbral` | `10` | Unidades desde las que se muestra *Disponible* (1–9 = *Pocas unidades*) |
| `--multiplo` | `50` | Redondeo comercial de los precios en COP |

Los multiplicadores de precio están en `scripts/lib/precios.py` y **deben coincidir** con
`src/data/precios.ts` (solo se usa para el texto informativo de `/interno/`).

---

## Estructura

```
scripts/                    generador del catálogo (Python)
  build_catalogo.py         CLI: Excel -> JSON
  lib/lector_excel.py       lectura y validación de la cabecera del ERP
  lib/normalizar.py         limpieza de texto, typos, nombres comerciales
  lib/especificaciones.py   parser de medida, grado, rosca, acabado, número de parte
  lib/taxonomia.py          tabla ERP -> líneas de producto públicas
  lib/precios.py            niveles de precio y redondeo
  tests/                    82 pruebas con casos reales del Excel

data/
  inventario ….xlsx         fuente de verdad
  generado/                 productos.json · productos-interno.json · lineas.json · reporte.json
  referencia/               material de marca original

public/datos/               índices que descarga el navegador
  buscador.json             2.790 referencias públicas (46 KB con gzip)
  interno.json              vista interna con costos y cantidades

src/
  pages/                    index · catalogo · lineas/[linea] · producto/[codigo] ·
                            nosotros · sectores · faq · contacto · noticias · interno · 404
  components/Catalogo.astro buscador y filtros (todo el JS del sitio)
  data/sitio.ts             datos de la empresa y textos editables
  data/colecciones.ts       colecciones transversales (inoxidable, clase 10.9…)
  content/noticias/         un .md por noticia
```

### Qué produce el script

| Archivo | Contiene | Se publica |
|---|---|---|
| `data/generado/productos.json` | Catálogo público completo, sin costo ni cantidad | No (solo build) |
| `data/generado/productos-interno.json` | + costo, cantidad, valor y los 4 niveles | No (solo build) |
| `data/generado/lineas.json` | Líneas, grupos, facetas y conteos | No (solo build) |
| `data/generado/reporte.json` | Fecha, totales e incidencias del Excel | No (solo build) |
| `public/datos/buscador.json` | Índice del buscador | **Sí** |
| `public/datos/interno.json` | Índice de la vista interna | **Sí** |

El JSON público **no contiene** el costo ni la cantidad: no se puede extraer de las herramientas
del navegador lo que no está en el archivo.

---

## Pendientes conocidos

### 1. `/interno/` no está protegida
Es la decisión tomada para esta prueba de concepto. Está marcada `noindex` y excluida del sitemap,
pero cualquiera con el enlace ve costos y márgenes. Antes de producción, protégela:

- **Vercel**: middleware con Basic Auth sobre `/interno` y `/datos/interno.json`.
- **Netlify**: `_headers` con `Basic-Auth`, o Netlify Identity.
- **Cloudflare Pages**: Cloudflare Access con política por correo.

### 2. Logotipo
El monograma del encabezado es una reconstrucción vectorial (`src/components/Logo.astro` y
`public/favicon.svg`). Reemplázalo por el logotipo original en SVG cuando esté disponible.

### 3. Tipografía
Se usa la pila de fuentes del sistema para no depender de un CDN. Para acercarse al gótico
condensado de la marca, descarga `Archivo Black` y `Archivo` en woff2 a `public/fuentes/` y añade
las reglas `@font-face` al inicio de `src/styles/global.css`; la variable `--display` ya está lista.

### 4. Imágenes
El sitio funciona sin fotografía (los iconos de línea son SVG). Faltan, en `public/img/`:

| Ruta | Uso |
|---|---|
| `img/lineas/*.jpg` | Bodegón por línea (opcional; hoy se usan los iconos) |
| `img/og.jpg` | Imagen 1200×630 para compartir en redes |
| `img/sectores/*.jpg` | Fotografía por sector |

Ya están integradas `img/marca/rinoceronte.jpeg` (página Nosotros) y
`img/marca/servicio-cliente.jpeg` (página Contacto).

### 5. Datos por confirmar
- **Horario de atención** y **NIT**: no aparecen en el sitio anterior; falta añadirlos al pie
  (`src/data/sitio.ts`).
- **21 referencias** sin medida reconocida y **5** con costo inválido: ver
  `data/generado/reporte.json`, sección `incidencias`. Conviene corregirlas en el ERP.

---

## Incidencias detectadas en el Excel del ERP

El generador las reporta en cada ejecución y las deja en `reporte.json`:

- **4 referencias con costo promedio negativo** y **1 en cero** → se publican como
  «Precio a confirmar».
- **1 descripción con un `|` extra**, que rompería un `split("|")` ingenuo.
- Errores de escritura consistentes: `TORNILOS BRISTOL`, `TUERCAS ` con espacio final,
  `MERCEDEZ`, `HIUNDAY`, `JHON DEER`, `TUERGA`, medidas con `1"""`.
- Sublíneas que no corresponden a la descripción (p. ej. una `VARILLA ROSCADA` clasificada como
  espárrago). El sitio respeta el ERP; corregirlo allá mejora el catálogo automáticamente.

Si el ERP agrega una línea nueva que la tabla de `taxonomia.py` no conoce, la referencia cae en
«Otros productos» y el script lo avisa por consola: nunca desaparece en silencio.

---

## Despliegue

Salida estática pura en `dist/`. Sirve con cualquier hosting estático:

```bash
make build
# publica dist/ en Vercel, Netlify, Cloudflare Pages o nginx
```

Antes de publicar en el dominio real, revisa que `site` en `astro.config.mjs` apunte a
`https://trackbolt.co` (es el valor por omisión) para que el sitemap y las canónicas salgan
correctas. La variable de entorno `TRACKBOLT_URL` lo sobreescribe.

---

## Demostración en AWS

`infra/` levanta la infraestructura para enseñarle el sitio al cliente sin tocar el dominio de
producción: un bucket de S3 **privado** como origen y una distribución de CloudFront por delante,
con HTTPS sobre el dominio `*.cloudfront.net`.

```bash
make infra-init      # una sola vez, descarga los proveedores
make infra-plan      # revisa qué se va a crear
make infra-aplicar   # crea bucket + distribución (~5 min por CloudFront)
make desplegar       # compila y sube; imprime la URL al terminar
```

Para bajarlo todo cuando termine la demo: `make infra-destruir`. El bucket lleva `force_destroy`,
así que no hay que vaciarlo a mano.

### Qué se crea

| Recurso | Papel |
|---|---|
| Bucket de S3 | Origen. Acceso público bloqueado; solo lo lee CloudFront. |
| Origin Access Control | Firma sigv4 las peticiones de CloudFront al bucket. |
| Política de bucket | Concede `s3:GetObject` únicamente a esta distribución (`AWS:SourceArn`). |
| CloudFront Function | Traduce `/catalogo/` a `/catalogo/index.html`. Sin esto todo daría 403. |
| Distribución | HTTPS obligatorio, compresión, cabeceras de seguridad, `404.html` en los errores. |

El estado de Terraform es **local** (`infra/terraform.tfstate`, ignorado por git). Para un solo
operador y una demo desechable es lo adecuado; si esto pasa a producción, migrar a un backend de S3
con bloqueo antes de que lo toque un segundo equipo.

### Qué hace `infra/desplegar.sh`

1. Lee bucket, ID de distribución y URL de las salidas de Terraform.
2. Compila con `TRACKBOLT_DEMO=1` (banner) y `TRACKBOLT_URL` (canónicas y sitemap apuntando a la
   demo, no a producción).
3. Sustituye `robots.txt` por un `Disallow: /` — la demo no debe indexarse ni competir con
   trackbolt.co en los buscadores.
4. Sube en dos pasadas: `/_astro/` con caché de un año inmutable, el resto con un minuto y
   revalidación. Cada pasada lleva su `--delete` acotado, así que borra lo que ya no existe.
5. Invalida la caché de CloudFront.

Opciones: `--catalogo` regenera antes el JSON desde el Excel, `--sin-invalidar` se salta la
invalidación, `--esperar` bloquea hasta que la invalidación se propague.

### El banner de demo

`TRACKBOLT_DEMO=1` activa `src/components/BannerDemo.astro`: franja superior con cintas de peligro,
sello fijo abajo a la izquierda y `noindex, nofollow` en todas las páginas. Sin esa variable el
sitio compila idéntico a producción. Para verlo en local, `make demo`.

### Advertencia sobre `/interno/`

La demo sube el sitio completo, **incluida `/interno/`** con costos, cantidades exactas y los cuatro
niveles de precio. La URL de CloudFront es pública: cualquiera que la tenga puede llegar a esa
página. Es una decisión consciente para esta demo — si hiciera falta cerrarla, las opciones son
excluir `/interno/` y `/datos/interno.json` de la subida, o poner Basic Auth en la
CloudFront Function.
