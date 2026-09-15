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
| Referencias en catálogo | **2.142** (inventario del ERP menos las líneas que no se publican) |
| Líneas de producto | **7** (de 11 posibles) |
| Páginas estáticas generadas | **2.159** (una por referencia + contenido) |
| Tiempo de build | ~3 s |
| JavaScript enviado al navegador | 4 KB · CSS 15 KB · índice de búsqueda 494 KB sin comprimir |
| Referencias con dibujo de referencia | **1.505** de 2.142 |
| Pruebas | 137 (pytest) |

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

`make imagenes` extrae los dibujos del catálogo PDF del fabricante; es una herramienta de un solo
uso y solo hay que repetirla si ese catálogo cambia.

`make todo` corre catálogo, pruebas y build. El manual completo de operación está en
[`trackbolt-web/README.md`](trackbolt-web/README.md).

---

## Cómo funciona

```
inventario total … .xlsx        reporte del ERP: qué existe, clasificación, descripción y costo
existencias adicionales … .xlsx extracción posterior: manda en cantidad y costo de lo nacional
inventario importacion … .xlsx  lista de importación: cruza cantidad y precio mayorista
data/imagenes.json              mapeo curado a mano: qué dibujo ilustra cada tipo de pieza
        │
        │   scripts/build_catalogo.py        ← Python: combina, cruza, excluye, clasifica, extrae especificaciones
        ▼
data/generado/*.json        catálogo público · catálogo interno · líneas · reporte
public/datos/*.json         índices que descarga el navegador
        │
        │   astro build                      ← 2.159 páginas estáticas
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

Cobertura sobre las 2.142 referencias publicadas: solo 5 quedan sin medida reconocida. Lo que el
parser no puede afirmar queda vacío en lugar de salir mal.

---

## Decisiones de producto

| Tema | Decisión |
|---|---|
| Catálogo | **El inventario del ERP manda**: se publica todo menos diez líneas que el cliente decidió no mostrar (pernos, espárragos y varillas, carriage, cabeza central, estufa, lámina, pines, remaches, chazos y herramienta). La lista de importación solo cruza existencias. |
| Precios | **El público no ve precios**: cotiza por WhatsApp o correo. Los cuatro niveles —mostrador, usuario final, almacén, mayorista— solo en `/interno/`; el mayorista es el `PRECIO UNIT` de la lista y los demás se derivan de él, sin redondeo. |
| Inventario | El cliente ve **estado sin cantidades**: *Disponible* (≥ 10 unidades), *Pocas unidades* (1–9), *Bajo pedido*. Las cantidades exactas solo en `/interno/`. |
| Clasificación | 11 líneas posibles por tipo de pieza, al estilo de boltdepot.com (7 con producto hoy), con filtros por diámetro, largo, grado, material, cabeza y rosca. |
| Existencias | Cuando dos reportes traen la misma referencia gana el más reciente; la lista de importación pisa la cantidad de lo que menciona. |
| Línea REX | Se muestra como **sello de calidad**, no como categoría aparte: quien busca «tornillo de zapata» ve las 117 juntas. |
| Imágenes | Dibujo de referencia **por tipo de pieza**, no por referencia: los códigos del catálogo del fabricante no coinciden con los del ERP. Un grupo sin mapear se queda sin dibujo a propósito — mejor una ficha sin figura que una con la figura equivocada. |
| Alcance | Catálogo navegable y cotización por WhatsApp. **Sin carrito ni pagos en línea.** |
| Vista interna | Publicada sin contraseña por decisión del cliente para esta prueba de concepto. Marcada `noindex` y fuera del sitemap. |

El redondeo de precios y el umbral de disponibilidad son parámetros del generador
(`--multiplo`, `--umbral`), no valores incrustados en el código.

El rojo de la marca está **medido sobre el logotipo del cliente**, no elegido a ojo: muestreando
`public/img/marca/logo.jpeg` da `#F30D10` en la palabra y `#EE0405` en el monograma. El token
`--rojo` (`#ed0c0f`) es el promedio de ambos y a la vez el mínimo oscurecimiento que alcanza 4,5:1
sobre blanco, el contraste que exige WCAG AA para texto pequeño. El rojo puro sobrevive como
`--rojo-vivo`, solo sobre negro.

---

## Estructura del repositorio

```
trackbolt-web/                  el proyecto
├─ scripts/                     generador del catálogo (Python) + 137 pruebas
├─ data/                        los Excel del ERP y los JSON generados
├─ src/                         páginas y componentes de Astro
├─ public/                      estáticos, dibujos de producto e índices del navegador
├─ infra/                       Terraform de la demo en AWS
├─ Makefile · README.md         comandos y manual de operación
│
CLAUDE.md                       guía de arquitectura para Claude Code
inventario/                     insumos originales: reportes del ERP, lista de
                                importación y el catálogo PDF del fabricante
logos/                          material de marca original (rinoceronte, logo, flyer)
```

Los archivos `transform_catalogo.py`, `catalogo_rex.html`, `correo_catalogo_rex.html` y
`existencias_*.xlsx` de la raíz son el **script anterior de un solo uso** y sus salidas. Quedan
como referencia histórica: `trackbolt-web/scripts/` los reemplazó.

---

## Hallazgos en los datos del ERP

El generador los reporta en cada corrida y los deja en `data/generado/reporte.json`. Conviene
corregirlos en el ERP: el catálogo mejora solo.

- **3 referencias con costo promedio negativo** y **3 en cero** → sin niveles de precio en
  `/interno/`, salvo que la lista de importación les fije el mayorista.
- **2 referencias con existencia negativa**, que el sitio muestra como «Bajo pedido».
- **1 descripción con un `|` extra**, que rompería un `split("|")` ingenuo.
- **5 referencias** cuya medida no es interpretable desde la descripción.
- En la lista de importación de septiembre: **12 códigos repetidos** con descripciones distintas
  (no se aplican) y **62 referencias REX** que la hoja no menciona, que conservan la cantidad de
  julio. Detalle en `reporte.json`, clave `fusion`.
- Errores de escritura consistentes: `TORNILOS BRISTOL`, `TUERCAS ` con espacio final, `TUERGA`,
  `MERCEDEZ`, `HIUNDAY`, `JHON DEER`, medidas escritas como `1"""`.
- Sublíneas que no corresponden a la descripción (una `VARILLA ROSCADA` clasificada como
  espárrago, por ejemplo). El sitio respeta lo que dice el ERP.

Descubrimiento aprovechado: **61 referencias traen el número de parte del fabricante de maquinaria**
(`6Y0846` de Caterpillar, `20Y3211210` de Komatsu, `4F3648`…). El catálogo permite buscar por ese
número, que es como realmente pide un mecánico de maquinaria pesada.

---

## Pendientes

1. **Logotipo vectorial.** El encabezado ya usa el logotipo real del cliente
   (`public/img/marca/logo.jpeg`), pero es un mapa de bits con el fondo negro incrustado — de ahí
   que `--negro` sea `#000000`. El favicon (`public/favicon.svg`) sigue siendo una reconstrucción.
   Ambos piden el vector original.
2. **Proteger `/interno/`** antes de producción: Basic Auth en el hosting o Cloudflare Access.
   La página ya lleva la advertencia.
3. **Tipografía.** Se usa la pila del sistema para no depender de un CDN. Para acercarse al gótico
   condensado de la marca, colocar `Archivo Black` en `public/fuentes/`; la variable `--display`
   ya está lista.
4. **Fotografía.** Las fichas ya llevan dibujo de referencia y la portada, Nosotros y Contacto
   usan el material de marca. Faltan los bodegones por línea, las fotos por sector y la imagen
   1200×630 para redes.
5. **Derechos de los dibujos de producto.** Salen del catálogo PDF del fabricante y se publican por
   decisión del proyecto; conviene que el cliente confirme el permiso con el proveedor antes de
   producción. Para quitarlos sin tocar código: `--imagenes ""` o vaciar `data/imagenes.json`.
6. **Datos de negocio.** Falta el horario de atención: el sitio anterior solo dice «Horario de
   oficina», sin días ni franjas. Agregarlo en `src/data/sitio.ts` cuando el cliente lo confirme.

---

## Publicación

Salida estática pura. Sirve en Vercel, Netlify, Cloudflare Pages o nginx.

```bash
cd trackbolt-web && make build     # resultado en dist/
```
