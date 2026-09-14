/**
 * Índices derivados del catálogo, calculados una sola vez por build.
 * Evita rearmar el mapa en cada una de las páginas de producto.
 */
import productosData from '../../data/generado/productos.json';

export const productos = productosData as any[];

const porGrupo = new Map<string, any[]>();
for (const p of productos) {
  const clave = `${p.linea}|${p.grupo}`;
  let lista = porGrupo.get(clave);
  if (!lista) {
    lista = [];
    porGrupo.set(clave, lista);
  }
  lista.push(p);
}

/** Referencias del mismo grupo, ordenadas por cercanía de medida. */
export function relacionados(producto: any, cuantos = 8): any[] {
  const lista = porGrupo.get(`${producto.linea}|${producto.grupo}`) ?? [];
  return lista
    .filter((p) => p.codigo !== producto.codigo)
    .sort(
      (a, b) =>
        Math.abs(a.orden_diametro - producto.orden_diametro) -
          Math.abs(b.orden_diametro - producto.orden_diametro) ||
        Math.abs(a.orden_largo - producto.orden_largo) -
          Math.abs(b.orden_largo - producto.orden_largo)
    )
    .slice(0, cuantos);
}
