/**
 * Colecciones transversales: no duplican datos, son el catálogo con un filtro puesto.
 * Reemplazan las colecciones del sitio anterior (tornillos, tuercas, pernos, inoxidable…).
 */
export const COLECCIONES = [
  {
    slug: 'inoxidable',
    nombre: 'Acero inoxidable',
    url: '/catalogo/?a=Inoxidable',
    descripcion:
      'Tornillería en acero inoxidable A2 (304) para ambientes corrosivos, industria de alimentos y exteriores.',
  },
  {
    slug: 'clase-10-9',
    nombre: 'Clase 10.9',
    url: '/catalogo/?r=Clase+10.9',
    descripcion: 'Alta resistencia, 1.000 MPa. El estándar de la maquinaria pesada moderna.',
  },
  {
    slug: 'clase-12-9',
    nombre: 'Clase 12.9',
    url: '/catalogo/?r=Clase+12.9',
    descripcion: 'La clase más alta de uso común, 1.200 MPa: rodaje, cuchillas y uniones críticas.',
  },
  {
    slug: 'grado-8',
    nombre: 'Grado 8 en pulgadas',
    url: '/catalogo/?r=Grado+8',
    descripcion: 'Equivalente SAE de la clase 10.9, para máquina y vehículo de origen americano.',
  },
  {
    slug: 'metrico',
    nombre: 'Sistema métrico',
    url: '/catalogo/?s=metrico',
    descripcion: 'Referencias en milímetros, con paso normal y paso fino.',
  },
  {
    slug: 'pulgadas',
    nombre: 'Sistema en pulgadas',
    url: '/catalogo/?s=pulgadas',
    descripcion: 'Referencias en pulgadas con rosca UNC y UNF, grados SAE 2, 5 y 8.',
  },
];
