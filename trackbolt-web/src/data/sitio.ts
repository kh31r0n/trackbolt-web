/**
 * Datos de la empresa y textos del sitio, en un solo lugar para poder editarlos
 * sin tocar las plantillas. Tomados de trackbolt.co y del material de marca.
 */

export const empresa = {
  nombre: 'Trackbolt',
  bajada: 'Tornillos para maquinaria pesada',
  lema: 'La fuerza que construye',
  lemaAlterno: 'No vendemos tornillos, vendemos soluciones',
  claim: 'Hechos para aguantar. Hechos para avanzar.',
  anios: '20+',
  descripcion:
    'Importación, distribución y fabricación de tornillería de alta resistencia para maquinaria pesada, ' +
    'industria y vehículos. Entregas a todo Colombia con asesoría técnica real.',
  direccion: 'Calle 6 #24-16, Ricaurte',
  ciudad: 'Bogotá, Colombia',
  email: 'operaciones@trackbolt.co',
  telefonos: [
    { etiqueta: 'WhatsApp principal', numero: '+57 310 816 8003', wa: '573108168003' },
    { etiqueta: 'WhatsApp alterno', numero: '+57 311 518 1728', wa: '573115181728' },
  ],
  redes: [
    { nombre: 'Instagram', url: 'https://www.instagram.com/importrackbolt/', usuario: '@importrackbolt' },
    { nombre: 'Facebook', url: 'https://www.facebook.com/profile.php?id=61568919667676', usuario: 'Trackbolt' },
  ],
  mision:
    'Conectar la industria con soluciones en tornillería confiables, entregadas con velocidad y ' +
    'asesoría experta, para que cada proyecto avance con fuerza y precisión.',
  vision:
    'En 2030, seremos la marca líder en soluciones de tornillería en Colombia, reconocida por ' +
    'revolucionar la experiencia del servicio industrial, con innovación, agilidad y relaciones ' +
    'que contribuyen al desarrollo del país.',
};

/** Enlace de WhatsApp con mensaje precargado. */
export function whatsapp(mensaje?: string, indice = 0): string {
  const wa = empresa.telefonos[indice].wa;
  return mensaje ? `https://wa.me/${wa}?text=${encodeURIComponent(mensaje)}` : `https://wa.me/${wa}`;
}

export const pilares = [
  {
    titulo: 'Fuerza',
    subtitulo: 'que sostiene',
    texto:
      'Clases 8.8, 10.9, 12.9 y 13.9 para uniones que trabajan a tracción y cortante sin ceder. ' +
      'Cada referencia entra al inventario con su grado verificado.',
  },
  {
    titulo: 'Resistencia',
    subtitulo: 'que no falla',
    texto:
      'Tornillería probada en tren de rodaje, cuchillas y ruedas: donde la vibración, el impacto ' +
      'y la abrasión rompen lo que no está a la altura.',
  },
  {
    titulo: 'Cercanía',
    subtitulo: 'que construye confianza',
    texto:
      'Asesoría técnica por WhatsApp, identificación de la referencia a partir de una foto o un ' +
      'número de parte, y despacho el mismo día en Bogotá.',
  },
];

export const sectores = [
  {
    slug: 'maquinaria-pesada',
    nombre: 'Maquinaria pesada y construcción',
    texto:
      'Excavadora, bulldozer, cargador y motoniveladora. Tornillo de zapata, de cuchilla y de ' +
      'segmento con equivalencia a número de parte del fabricante.',
    lineas: ['rodaje-zapata-cuchilla', 'tornillos-hexagonales', 'tuercas'],
  },
  {
    slug: 'transporte-de-pasajeros',
    nombre: 'Transporte público de pasajeros',
    texto:
      'Flotas de bus y camión: pernos y espárragos de rueda por marca de vehículo, tuercas cónicas ' +
      'y tornillería de chasis y suspensión.',
    lineas: ['pernos-rueda', 'tuercas', 'arandelas'],
  },
  {
    slug: 'agroindustria',
    nombre: 'Agroindustria',
    texto:
      'Tractor, cosechadora e implemento agrícola. Tornillería de arado, discos y cuchillas, más ' +
      'inoxidable para plantas de proceso.',
    lineas: ['rodaje-zapata-cuchilla', 'esparragos-varillas', 'tornillos-hexagonales'],
  },
  {
    slug: 'industria-general',
    nombre: 'Industria y mantenimiento',
    texto:
      'Montaje estructural, mantenimiento de planta y fabricación especial bajo plano, con ' +
      'herramienta profesional para el taller.',
    lineas: ['tornillos-bristol', 'arandelas', 'herramienta'],
  },
];

export const diferenciales = [
  {
    titulo: 'Entregas en tiempo récord',
    texto: 'Bogotá y alrededores en 1 a 2 días hábiles. Resto del país entre 2 y 5 días hábiles.',
  },
  {
    titulo: 'Stock programado',
    texto: 'Gestionamos existencias por cliente para que la referencia crítica nunca detenga la producción.',
  },
  {
    titulo: 'Fabricación especial',
    texto: 'Lo que no existe en el mercado lo fabricamos bajo plano o contra muestra física.',
  },
  {
    titulo: 'Sin pedido mínimo',
    texto: 'Desde una unidad hasta el volumen de un proyecto, con descuento por cantidad.',
  },
];

export const faq = [
  {
    p: '¿Cómo leo la medida de un tornillo?',
    r: 'En sistema métrico se escribe M{diámetro} × {largo} y el paso en milímetros: un M16 × 120 con paso 2.00 ' +
       'tiene 16 mm de diámetro, 120 mm de largo y 2 mm entre hilos. En pulgadas se escribe {diámetro} × {largo}: ' +
       'un 5/8" × 2" mide 5/8 de pulgada de diámetro y 2 pulgadas de largo, y la rosca se identifica como UNC ' +
       '(ordinaria) o UNF (fina). En nuestro catálogo puedes filtrar directamente por diámetro y largo.',
  },
  {
    p: '¿Qué significan 8.8, 10.9 y 12.9?',
    r: 'Es la clase de resistencia del sistema métrico. El primer número por 100 es la resistencia a la tracción ' +
       'en MPa y el segundo indica qué fracción de esa resistencia es el límite elástico. Un 8.8 resiste 800 MPa, ' +
       'un 10.9 llega a 1.000 MPa y un 12.9 a 1.200 MPa. A mayor clase, mayor carga admisible y menor ductilidad: ' +
       'un 12.9 no se debe usar donde se espera deformación antes de la falla.',
  },
  {
    p: '¿Y los grados SAE 2, 5 y 8?',
    r: 'Son el equivalente en pulgadas. El grado 2 es acero de bajo carbono sin tratamiento, el grado 5 es templado ' +
       'y revenido (equiparable a un 8.8) y el grado 8 es de aleación tratada (cercano a un 10.9). Se reconocen por ' +
       'las marcas radiales en la cabeza: sin marcas el 2, tres marcas el 5 y seis marcas el 8.',
  },
  {
    p: '¿Cuál es la diferencia entre rosca parcial y rosca total?',
    r: 'La rosca parcial deja una parte lisa del vástago junto a la cabeza. Esa zona lisa trabaja mejor a cortante ' +
       'y centra la unión, por eso es la habitual en maquinaria. La rosca total llega hasta la cabeza y sirve cuando ' +
       'se necesita apriete en todo el largo o el agarre es variable.',
  },
  {
    p: '¿Puedo pedir por número de parte del fabricante?',
    r: 'Sí. Buena parte de nuestras referencias de rodaje están cruzadas con el número de parte del fabricante de ' +
       'maquinaria (por ejemplo 6Y0846, 9W3619 o 4F3648). Escríbelo en el buscador del catálogo y, si lo tenemos ' +
       'referenciado, aparece directo. Si no, envíanos el número por WhatsApp y lo identificamos.',
  },
  {
    p: '¿Dónde están ubicados?',
    r: 'En la Calle 6 #24-16, barrio Ricaurte, Bogotá. Desde ahí despachamos a todo el país y puedes recoger tu ' +
       'pedido coordinándolo antes por WhatsApp al +57 310 816 8003.',
  },
  {
    p: '¿Realizan envíos a todo el país?',
    r: 'Sí, a cualquier ciudad o municipio de Colombia con transportadoras aliadas. Bogotá y alrededores reciben en ' +
       '1 a 2 días hábiles; el resto del país entre 2 y 5 días hábiles, con variación en temporada alta.',
  },
  {
    p: '¿Cuál es el pedido mínimo?',
    r: 'No exigimos pedido mínimo en la mayoría de los productos. Para volumen manejamos descuento por cantidad: ' +
       'pídelo al cotizar.',
  },
  {
    p: '¿Los productos tienen garantía?',
    r: 'Todos nuestros productos están cubiertos por garantía contra defectos de fabricación. Si detectas una ' +
       'anomalía, contáctanos dentro del periodo de garantía con el código de la referencia y la factura.',
  },
  {
    p: '¿Qué métodos de pago aceptan?',
    r: 'Tarjetas de crédito y débito, transferencia bancaria, Nequi, Daviplata y efectivo en puntos autorizados.',
  },
  {
    p: '¿Fabrican referencias que no existen en el mercado?',
    r: 'Sí. Fabricamos bajo plano o contra muestra física: espárragos especiales, tornillos de medida no comercial, ' +
       'largos fuera de estándar y piezas con acabado específico. Envíanos el plano o la pieza y cotizamos.',
  },
  {
    p: '¿El precio del catálogo es el final?',
    r: 'El precio publicado es el precio al público en pesos colombianos e incluye la referencia por unidad. ' +
       'Para volumen, obra o distribución manejamos precios diferenciales; escríbenos y te pasamos la cotización.',
  },
];
