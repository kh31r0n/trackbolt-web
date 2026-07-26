/**
 * Marca la compilación como demostración.
 *
 * Se activa con `TRACKBOLT_DEMO=1` en el entorno de compilación; `infra/desplegar.sh`
 * lo exporta al construir para el bucket de S3. En una compilación normal la bandera
 * queda en falso y el sitio sale idéntico a producción.
 */

const entorno: Record<string, string | undefined> =
  typeof process !== 'undefined' && process.env ? process.env : {};

export const ES_DEMO = entorno.TRACKBOLT_DEMO === '1';

export const demo = {
  etiqueta: 'Página demo',
  mensaje: 'Versión de demostración de trackbolt.co — datos del inventario del 25/07/2026.',
  sello: 'Demo',
};
