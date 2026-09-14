# Trackbolt — sitio web y catálogo

Sitio estático en **Astro** cuyo catálogo se genera con un **script de Python** a partir de los
reportes de existencias del ERP. Reemplaza a trackbolt.co.

- **2.142 referencias**, 7 líneas de producto, una página estática por referencia (2.159 páginas).
- **Sin precios en el sitio público**: el cliente cotiza por WhatsApp o correo.
- **Disponibilidad sin cantidades** para el cliente; cantidades, costos y los cuatro niveles de
  precio solo en `/interno/`.
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

**El inventario define qué referencias existen.** El generador lee tres archivos de `data/`:

- **Reporte de existencias del ERP** (`inventario total … .xlsx`, columnas `Bodega | Tipo | Linea |
  Sublinea | Producto | Unidad medida | Cantidad | Total | Promedio`). Es la base y el **único**
  archivo que trae la línea REX.
- **Existencias adicionales** (`existencias adicionales … .xlsx`, las mismas columnas más
  `Ubicacion`). Es una extracción posterior de la tornillería nacional: **manda sobre la base** en
  las referencias que traen las dos (cantidad y costo más recientes) y agrega las que faltaban.
  Las columnas se buscan por nombre, así que la columna de más no corre los datos de lugar.
- **Lista de importación** (`inventario importacion … .xlsx`, columnas `DESCRIPCION DEL PRODUCTO |
  CANT | PRECIO UNIT | TOTAL`, con títulos de sección y el código pegado a la descripción). **Solo
  cruza existencias**: aporta la cantidad y `PRECIO UNIT`, que es el **precio mayorista**; de él
  salen los otros tres niveles (base = mayorista ÷ 1,5). Lo que la lista no menciona conserva la
  existencia del inventario; un código repetido en la hoja no se aplica. Todo queda en
  `reporte.json`, clave `fusion`.

Al final se descartan las líneas del ERP que el cliente no publica (`taxonomia.LINEAS_EXCLUIDAS`:
pernos, espárragos y varillas, carriage, cabeza central, estufa, lámina, pines, remaches, chazos y
toda la herramienta). El recuento por línea queda en `reporte.json`, clave `excluidas`.

1. Copia el archivo nuevo a `data/` (mismo formato de columnas que el que reemplaza).
2. Ajusta la constante `EXCEL`, `ADICIONALES` o `IMPORTACION` en `scripts/build_catalogo.py`, o
   pásalo por parámetro:

```bash
make catalogo
# o bien
../.venv/bin/python scripts/build_catalogo.py --excel "data/inventario 2026-10.xlsx" --adicionales ""
```

3. Revisa el resumen que imprime el script (referencias combinadas, excluidas, incidencias,
   sublíneas sin clasificar, resultado de la fusión).
4. `make build` y publica `dist/`.

Cuando llegue un reporte completo del ERP posterior a estos, pásalo con `--excel` y
`--adicionales ""`: un solo archivo basta y no hace falta combinar nada.

```bash
make todo      # catalogo + pruebas + build
```

### Parámetros del generador

| Parámetro | Def. | Qué hace |
|---|---|---|
| `--excel` | `data/inventario total trackbolt 07-25-26.xlsx` | Reporte de existencias base |
| `--adicionales` | `data/existencias adicionales 09-14-26.xlsx` | Reporte posterior que manda sobre la base en lo que traen los dos (`""` = no aplicar) |
| `--importacion` | `data/inventario importacion 09-02-26.xlsx` | Lista de importación que cruza existencias: cantidad y precio mayorista (`""` = no aplicar) |
| `--imagenes` | `data/imagenes.json` | Mapeo curado de imágenes de referencia por línea y grupo (`""` = no aplicar) |
| `--salida` | `data/generado` | Carpeta de los JSON |
| `--umbral` | `10` | Unidades desde las que se muestra *Disponible* (1–9 = *Pocas unidades*) |
| `--multiplo` | `0` | Múltiplo de redondeo comercial en COP; `0` = sin redondeo, se conservan los centavos |

Los multiplicadores de precio están en `scripts/lib/precios.py` y **deben coincidir** con
`src/data/precios.ts` (solo se usa para el texto informativo de `/interno/`).

---

## Estructura

```
scripts/                    generador del catálogo (Python)
  build_catalogo.py         CLI: Excel -> JSON
  lib/lector_excel.py       lectura del ERP; resuelve las columnas por nombre
  lib/inventario.py         combina los dos reportes de existencias
  lib/lector_importacion.py lectura de la lista de importación
  lib/fusion.py             cruce de la lista con el inventario
  lib/normalizar.py         limpieza de texto, typos, nombres comerciales
  lib/especificaciones.py   parser de medida, grado, rosca, acabado, número de parte
  lib/taxonomia.py          tabla ERP -> líneas públicas y líneas excluidas
  lib/precios.py            niveles de precio y redondeo
  lib/imagenes.py           imagen de referencia por línea y grupo
  extraer_imagenes_pdf.py   saca los dibujos del catálogo PDF del fabricante (uso puntual)
  tests/                    137 pruebas con casos reales del Excel

data/
  inventario ….xlsx         fuente de verdad (existencias del ERP + lista de importación)
  generado/                 productos.json · productos-interno.json · lineas.json · reporte.json
  imagenes.json             mapeo curado grupo -> dibujo (se edita a mano)
  referencia/               material de marca original

public/datos/               índices que descarga el navegador
  buscador.json             2.142 referencias públicas (494 KB sin comprimir)
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
| `data/generado/productos.json` | Catálogo público completo, sin costo, cantidad ni precio | No (solo build) |
| `data/generado/productos-interno.json` | + costo, cantidad, valor y los 4 niveles | No (solo build) |
| `data/generado/lineas.json` | Líneas, grupos, facetas y conteos | No (solo build) |
| `data/generado/reporte.json` | Fecha, totales e incidencias del Excel | No (solo build) |
| `public/datos/buscador.json` | Índice del buscador | **Sí** |
| `public/datos/interno.json` | Índice de la vista interna | **Sí** |

El JSON público **no contiene** el costo, la cantidad ni el precio: no se puede extraer de las
herramientas del navegador lo que no está en el archivo.

---

## Imágenes de producto

Las fichas muestran un dibujo de referencia sacado del catálogo PDF del fabricante
(`inventario/catalogs/`). Los códigos de ese catálogo son del fabricante y **no coinciden** con los
del ERP, así que la imagen no se asocia por referencia sino por **tipo de pieza**: la pareja
línea/grupo de la taxonomía. Un mismo dibujo ilustra todas las referencias de su grupo, y por eso
la ficha lleva el pie «Imagen de referencia».

```bash
make imagenes        # extrae los dibujos del PDF a public/img/productos/
open data/generado/imagenes-fey.html   # hoja de contactos para curar el mapeo
make catalogo        # vuelca la imagen elegida en productos.json
```

- `scripts/extraer_imagenes_pdf.py` descarta el cromo de la maqueta (todo lo que se repite entre
  páginas), las páginas sin número de ítem y lo que no tiene tamaño de dibujo. Deja 209 imágenes,
  el inventario en `data/generado/imagenes-fey.json` y la hoja de contactos en HTML. Necesita
  `pymupdf` en el venv.
- `data/imagenes.json` es el mapeo **curado a mano**: `"linea|grupo" -> ruta`. Un grupo sin entrada
  se queda sin imagen a propósito: es preferible una ficha sin dibujo a una con el dibujo
  equivocado. Por eso `por_linea` está vacío — dentro de una línea conviven formas muy distintas
  (mariposa, uña, ciega) y un respaldo genérico mentiría.
- Hoy quedan ilustradas 1.505 de 2.142 referencias. Sin cobertura: arandelas y tornillos Bristol
  (el catálogo del fabricante no los trae). `reporte.json`, clave `imagenes`, lleva la cuenta y la
  lista de grupos sin mapear.
- La imagen viaja en `productos.json` y `productos-interno.json`, **no** en `buscador.json`: el
  índice que descarga el navegador no crece.

---

## Pendientes conocidos

### 1. `/interno/` no está protegida
Es la decisión tomada para esta prueba de concepto. Está marcada `noindex` y excluida del sitemap,
pero cualquiera con el enlace ve costos y márgenes. Antes de producción, protégela:

- **Vercel**: middleware con Basic Auth sobre `/interno` y `/datos/interno.json`.
- **Netlify**: `_headers` con `Basic-Auth`, o Netlify Identity.
- **Cloudflare Pages**: Cloudflare Access con política por correo.

### 2. Logotipo
El encabezado usa el logotipo real del cliente (`public/img/marca/logo.jpeg`, referenciado desde
`src/components/Logo.astro`). Pendiente: el favicon (`public/favicon.svg`) sigue siendo una
reconstrucción; reemplázalo cuando haya una versión vectorial del logo.

### 3. Tipografía
Se usa la pila de fuentes del sistema para no depender de un CDN. Para acercarse al gótico
condensado de la marca, descarga `Archivo Black` y `Archivo` en woff2 a `public/fuentes/` y añade
las reglas `@font-face` al inicio de `src/styles/global.css`; la variable `--display` ya está lista.

### 4. Imágenes
Las fichas de producto ya muestran un **dibujo de referencia** por tipo de pieza (ver «Imágenes de
producto» más abajo). Siguen faltando, en `public/img/`:

| Ruta | Uso |
|---|---|
| `img/lineas/*.jpg` | Bodegón por línea (opcional; hoy se usan los iconos) |
| `img/og.jpg` | Imagen 1200×630 para compartir en redes |
| `img/sectores/*.jpg` | Fotografía por sector |

Ya están integradas `img/marca/mascota-home.jpeg` (mascota protagonista de la portada del home),
`img/marca/rinoceronte.jpeg` (página Nosotros) y `img/marca/servicio-cliente.jpeg` (página
Contacto).

### 5. Derechos de las imágenes de producto
Los dibujos salen del catálogo PDF del fabricante (`inventario/catalogs/`). Se publican por decisión
explícita del proyecto, pero **conviene que el cliente confirme con el proveedor el derecho de uso
antes de producción**. Para quitarlos del sitio sin tocar código, basta con vaciar
`data/imagenes.json` (o generar con `--imagenes ""`): las fichas vuelven a renderizarse sin figura.

### 6. Datos por confirmar
- **Horario de atención**: el sitio anterior solo dice «Horario de oficina», sin días ni franjas.
  Falta pedírselo al cliente y añadirlo a `src/data/sitio.ts`. Mientras falte, el JSON-LD no puede
  pasar de `Organization` a `LocalBusiness` (necesita `openingHoursSpecification`).
- **62 referencias REX** que la lista de importación no menciona: conservan la cantidad de julio.
  Ver `reporte.json`, clave `fusion.rex_sin_cobertura`.
- **12 códigos repetidos** en la lista de importación con descripciones distintas: no se aplican y
  conservan la cantidad del inventario (`reporte.json`, clave `fusion.duplicados`).
- **719 referencias excluidas** del catálogo por línea (`reporte.json`, clave `excluidas`): 392 de
  herramienta, 185 pernos, 49 espárragos y varillas, 35 carriage, 28 cabeza central, 12 estufa,
  8 pines, 6 remaches, 2 chazos y 2 de lámina. Para que alguna vuelva, quítala de
  `taxonomia.LINEAS_EXCLUIDAS`.

---

## Incidencias detectadas en el Excel del ERP

El generador las reporta en cada ejecución y las deja en `reporte.json`:

- **3 referencias con costo promedio negativo** y **3 en cero**: se publican sin niveles de precio
  en `/interno/`, salvo que la lista de importación les fije el mayorista.
- **2 referencias con existencia negativa**, que el sitio muestra como «Bajo pedido».
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

## Publicación en AWS

`infra/` levanta la infraestructura del sitio: un bucket de S3 **privado** como origen y una
distribución de CloudFront por delante, con HTTPS sobre el dominio `*.cloudfront.net`. Sirve tanto
para enseñarle el sitio al cliente sin tocar el dominio de producción como para publicarlo de
verdad; la diferencia la marca la variable `entorno`.

```bash
make infra-init      # una sola vez, descarga los proveedores
make infra-plan      # revisa qué se va a crear
make infra-aplicar   # crea bucket + distribución (~5 min por CloudFront)
make desplegar       # compila y sube; imprime la URL al terminar
```

Para bajarlo todo cuando termine la demo: `make infra-destruir`. En el entorno `demo` el bucket
lleva `force_destroy`, así que no hay que vaciarlo a mano.

### La cuenta de AWS

Todo vive en la cuenta **006392690655**, en `us-east-1`. El proveedor lleva
`allowed_account_ids = [var.cuenta_aws]` y `desplegar.sh` contrasta `sts get-caller-identity` con la
salida `cuenta` de Terraform, así que **ejecutar con las credenciales de otra cuenta aborta antes de
tocar nada**.

Esa guardia existe por un incidente concreto: el nombre del bucket es único global, de modo que unas
credenciales ajenas no dan «no existe» sino 403, y CloudFront simplemente no encuentra la
distribución. El refresco borra los recursos del plan y Terraform propone recrearlo todo —
duplicando la infraestructura en la cuenta equivocada y dejando huérfana la real. El valor va
versionado en `variables.tf` a propósito: `*.tfvars` está en `.gitignore` y no sobreviviría a un
clon nuevo.

### Entornos

`entorno` admite `demo` (predeterminado) y `produccion`:

| | `demo` | `produccion` |
|---|---|---|
| `force_destroy` en el bucket | sí | no — un `destroy` accidental falla en vez de borrar |
| Banner de demo (`TRACKBOLT_DEMO=1`) | sí | no |
| `robots.txt` | se sustituye por `Disallow: /` | el de `public/`, con el sitemap real |

El estado es local y la demo actual vive en el workspace `default`. Si algún día conviven los dos
entornos, hay que crear un workspace **para el nuevo** (`terraform workspace new produccion`) y
dejar el existente donde está: cambiar de workspace con la demo dentro daría un estado vacío y
dejaría huérfano todo lo creado.

### Qué se crea

| Recurso | Papel |
|---|---|
| Bucket de S3 | Origen. Acceso público bloqueado; solo lo lee CloudFront. |
| Versionado + ciclo de vida | Permite revertir un despliegue malo; las versiones antiguas caducan a los 30 días y las subidas multiparte incompletas a los 7. |
| Origin Access Control | Firma sigv4 las peticiones de CloudFront al bucket. |
| Política de bucket | Concede `s3:GetObject` únicamente a esta distribución (`AWS:SourceArn`). |
| CloudFront Function | Traduce `/catalogo/` a `/catalogo/index.html`. Sin esto todo daría 403. |
| Distribución | HTTPS obligatorio, compresión, cabeceras de seguridad, `404.html` en los errores. |

El estado de Terraform es **local** (`infra/terraform.tfstate`, ignorado por git). Para un solo
operador es lo adecuado; si lo llega a tocar un segundo equipo, migrar a un backend de S3 con
bloqueo antes.

### Credenciales para que otro actualice el portal

`crear_usuario_despliegue` (activo por omisión) crea un usuario de IAM,
`trackbolt-demo-despliegue`, con una clave de acceso y **solo** estos permisos:

| Sobre | Acciones |
|---|---|
| El bucket del sitio | `s3:ListBucket` |
| Su contenido | `s3:GetObject`, `PutObject`, `DeleteObject`, `AbortMultipartUpload` |
| Esta distribución | `cloudfront:CreateInvalidation`, `GetInvalidation` |

Nada más: no puede listar los buckets de la cuenta, ni borrar este, ni leer o
modificar la distribución. Las claves se leen con `terraform output -raw clave_despliegue_id` y
`terraform output -raw clave_despliegue_secreta` (esta última va marcada como sensible, así que no
aparece en el `apply`).

Quien las reciba **no tendrá el `terraform.tfstate`**, que está en `.gitignore`. Por eso
`desplegar.sh` acepta los mismos datos por variables de entorno y, si están las siete, no llama a
Terraform en ningún momento:

```bash
export AWS_ACCESS_KEY_ID=…  AWS_SECRET_ACCESS_KEY=…
export TRACKBOLT_BUCKET=trackbolt-demo-8942c2b5 \
       TRACKBOLT_DISTRIBUCION=E2WRXJVQ13TR1R \
       TRACKBOLT_URL=https://d30ye8hh8i6gmx.cloudfront.net \
       TRACKBOLT_REGION=us-east-1 \
       TRACKBOLT_ENTORNO=demo \
       TRACKBOLT_CUENTA=006392690655 \
       TRACKBOLT_PUBLICAR_INTERNO=true
./infra/desplegar.sh
```

Para **revocar** el acceso cuando termine: `crear_usuario_despliegue = false` y `make infra-aplicar`.
Para **rotar** la clave: `terraform -chdir=infra taint aws_iam_access_key.despliegue[0]` y aplicar.

El secreto queda en el `terraform.tfstate` local, que es texto plano. Está en `.gitignore`, pero
conviene no copiarlo a ningún sitio compartido.

### Qué hace `infra/desplegar.sh`

1. Lee bucket, distribución, URL, entorno y cuenta de las salidas de Terraform, y **comprueba que
   las credenciales son de esa cuenta** antes de seguir.
2. Compila con `TRACKBOLT_URL` (canónicas y sitemap apuntando a este sitio) y, en el entorno `demo`,
   con `TRACKBOLT_DEMO=1` para el banner.
3. En `demo`, sustituye `robots.txt` por un `Disallow: /` — la demo no debe indexarse ni competir
   con trackbolt.co en los buscadores.
4. Sube en dos pasadas: `/_astro/` con caché de un año inmutable, el resto con un minuto y
   revalidación. Cada pasada lleva su `--delete` acotado, así que borra lo que ya no existe.
   Las exclusiones comunes van en un array compartido: si una pasada excluyera algo que la otra no,
   borraría lo que la otra acaba de subir.
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
página. Es una decisión consciente para esta demo.

Para cerrarla basta con `publicar_interno = false`: `desplegar.sh` lee esa salida y excluye
`interno/*` y `datos/interno.json` de las dos pasadas de subida. La alternativa, si hiciera falta
que la página exista pero protegida, es Basic Auth en la CloudFront Function.
