# Catálogos de referencia

Catálogos externos que se consultan a mano. **Ninguno entra al pipeline** de
`scripts/build_catalogo.py`; la única excepción es el catálogo del proveedor Fey, que
`scripts/extraer_imagenes_pdf.py` lee una sola vez para sacar los dibujos de línea.

| Archivo | Qué es | Uso |
|---|---|---|
| `124-catalago-de-produtos-fey.pdf` | Catálogo del proveedor Fey, 215 pp | Fuente de `public/img/productos/` vía `make imagenes` |
| `cat-one-safe-source-2019.pdf` | Cat® One Safe Source 2019, 700 pp | Referencia de partes Caterpillar |
| `cat-one-safe-source-2017-2018.pdf` | Cat® One Safe Source 2017-2018, 618 pp | Referencia de partes Caterpillar |
| `cat-one-safe-source-2015-2016.pdf` | Cat® One Safe Source 2015-2016, 574 pp | Referencia de partes Caterpillar |
| `cat-cucharones-excavadoras-hidraulicas.pdf` | Cucharones para excavadoras hidráulicas, 43 pp, español | Familias de varillaje y tablas GET vigentes |
| `cat-cucharones-de-excavacion.pdf` | Ficha de cucharones de excavación, 4 pp, español | Complemento del anterior |

Todos son material con copyright de Caterpillar Inc. o de Fey. Están aquí como referencia
interna; no se republican en el sitio.

---

## Cat® One Safe Source (catálogo de partes de alta rotación)

Es el catálogo que los concesionarios Cat publican con las piezas de mayor rotación:
número de parte, descripción, medidas y tablas de equivalencia. La versión en español se
llama **«Su Única Fuente Segura»**.

### De dónde salió cada uno

| Edición | Origen |
|---|---|
| 2019 | <https://www.westernstatescat.com/wp-content/uploads/2021/11/OneSafeSource-parts-2019.pdf> |
| 2017-2018 | <https://www.westernstatescat.com/wp-content/uploads/2019/05/One-Safe-Source-PECP9067-06_LR-2017-2018.pdf> |
| 2015-2016 | <https://www.finning.com/content/dam/finning/en_ca/Documents/Parts/one%20safe%20source%202015-2016.pdf> |

Páginas de concesionario que lo ofrecen y suelen apuntar a la edición más reciente:

- Milton CAT — <https://www.miltoncat.com/parts/one-safe-source-parts-catalog>
- HO Penn — <https://www.hopenn.com/parts/parts-catalog/>

### Secciones de la edición 2019

Los números son la **página impresa**; en el PDF hay que sumarle 2.

| Sección | Pág. |
|---|---|
| Introduction | 5 |
| Batteries and Electrical Parts | 7 |
| Bearings | 133 |
| Cylinder Seals | 141 |
| Engine Parts | 211 |
| Equipment Fluids | 239 |
| Filters | 287 |
| Ground Engaging Tools | 301 |
| Hardware | 465 |
| Operator Environment | 537 |
| O-Rings | 575 |
| Tires | 605 |
| Undercarriage | 617 |
| Yellowmark™ | 651 |
| Parts Catalog References | 697 |

Subsecciones de **Ground Engaging Tools** (herramientas de corte), que es el capítulo más
grande:

| Subsección | Pág. |
|---|---|
| Backhoe Loaders | 302 |
| Bulldozers / Compactors | 311 |
| Rippers / Scarifiers | 342 |
| Compact Construction Equipment | 348 |
| Skid Steer Loaders | 361 |
| Excavators | 366 |
| Excavator Tips — K Series™ | 373 |
| Excavator Tips — Side Pin Style | 377 |
| Excavator Sidecutters | 380 |
| Loaders | 384 |
| Motor Graders | 439 |
| Paving Products | 451 |
| Scrapers | 453 |

### Cobertura de capítulos

Contra la lista de ocho capítulos que se buscaba originalmente, la edición 2019 cubre cinco:

| Capítulo buscado | ¿Está? | Dónde |
|---|---|---|
| Baterías y repuestos eléctricos | sí | *Batteries and Electrical Parts*, p. 7 |
| Filtros | sí | *Filters*, p. 287 |
| Herramientas de corte | sí | *Ground Engaging Tools*, p. 301 |
| Retroexcavadoras cargadoras | sí | *Backhoe Loaders*, p. 302 (dentro de GET) |
| Tractores topadoras / compactadores | sí | *Bulldozers/Compactors*, p. 311 (dentro de GET) |
| Sistemas de enfriamiento | parcial | refrigerantes en *Equipment Fluids* → Coolants, p. 271 |
| Productos químicos, compuestos y pinturas | parcial | algo en *Equipment Fluids*, p. 239 |
| Sistemas de admisión de aire y escape | no | solo filtros de aire dentro de *Filters* |

Esos ocho nombres coinciden casi literalmente con las **categorías de la tienda en línea**
de Cat, no con el índice del PDF:

- <https://parts.cat.com/es/catcorp/shop-all-categories>
- <https://parts.cat.com/es/catcorp/category/engine-cooling-system>

Si hace falta el árbol completo con esos nombres exactos, la fuente es la tienda, no un
catálogo impreso.

---

## Cucharones y familias de varillaje

Documentos oficiales de Caterpillar en español, bajados del CDN de Cat:

- **Cucharones para excavadoras hidráulicas** (43 pp) —
  <https://s7d2.scene7.com/is/content/Caterpillar/CM20190118-46340-00228>
  Trae el cuadro de referencia cruzada de familias de varillaje (diámetro de pasador del
  brazo y del eslabón, extensión vertical y del pasador) para excavadoras pequeñas,
  medianas, grandes y de ruedas, más las tablas de puntas Cat Advansys™.
- **Cucharones de excavación** (4 pp) —
  <http://s7d2.scene7.com/is/content/Caterpillar/CM20190222-49168-63683>

### Nomenclatura: vieja contra nueva

Caterpillar clasifica los cucharones por la **familia de varillaje** al final del brazo.
La nomenclatura cambió y los dos sistemas circulan mezclados:

| | Familias | Puntas |
|---|---|---|
| Catálogos viejos (≈2008-2013) | Varillaje B, C, D | Serie J: J300, J350, J400, J460 |
| Catálogos actuales | 312, A, B, CB, DB, TB, UB, VB2, WB2, HB2, JC | Serie K y Advansys™ |

Como referencia aproximada: varillaje B ≈ clase 320, C ≈ 325, D ≈ 330.

Las tablas viejas ordenaban los cucharones por varillaje; la edición 2019 reorganizó la
misma información por **espesor de la cuchilla de base** (*Excavators*, p. 366-372). Los
números de parte siguen siendo los mismos.

### Ojo con `6I-` contra `61-`

Varios adaptadores Cat empiezan con **`6I-`, letra I mayúscula, no el dígito uno**. En
OCR y en transcripciones automáticas aparecen mal casi siempre:

| Correcto | Error frecuente |
|---|---|
| `6I-6354`, `6I-6355`, `6I-6356` | `61-6354`, `61-6355`, `61-6356` |
| `6I-6404`, `6I-6405`, `6I-6406` | `61-6404`, `61-6405`, `61-6406` |
| `6I-5303` | `61-5303` |

Se verifica en `cat-one-safe-source-2019.pdf`, página impresa 376 (PDF 378), tabla
«K Family Identification»: los adaptadores HEX de dos correas son 6I-6354/6I-6355/6I-6356
para J350 y 6I-6404/6I-6405/6I-6406 para J400.

El mismo cuidado aplica a otros prefijos con letra: `9R-`, `4F-`, `4K-`, `8E-`, `6Y-`,
`7Y-`, `1U-`, `9C-`, `5V-`, `8K-`, `7I-`, `8U-`, `5W-`.

---

## La versión en español: no se descargó

La edición en español, **«Su Única Fuente Segura»**, existe al menos en 2006-2007,
2008-2009, 2013-2014 y 2014, pero ningún concesionario la publica en abierto. Las únicas
copias localizadas están en sitios de documentos subidos por usuarios:

- Scribd — <https://www.scribd.com/doc/50122708/Fuente-segura-caterpillar-2008-2009-espanol>
- idoc.pub — <https://idoc.pub/documents/fuente-segura-caterpillar-2008-2009-espaol-8jlkg6921zn5>
- pdfcoffee — <https://pdfcoffee.com/fuente-segura-cat-2013-pdf-free.html>
- vbook — <https://vbook.pub/documents/fuente-segura-caterpillar-version-2014-pdfpdf-j20l7qke592m>

Son resubidas sin autorización de material con copyright de Caterpillar. Además, el botón
de descarga de idoc.pub no apunta al archivo: pasa por un redirector publicitario
(`adexchangerapid.com`). **No se bajó ninguna.**

La vía limpia para conseguirla es pedirla al concesionario Cat. En Colombia es
**Gecolsa**.
