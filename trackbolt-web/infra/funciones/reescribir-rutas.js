// CloudFront Function (petición del visor).
//
// Astro compila con URLs de directorio: /catalogo/ vive en catalogo/index.html.
// El origen REST de S3 no resuelve documentos índice por carpeta, así que aquí
// se completa la clave antes de consultar la caché.
//
//   /                    -> /index.html   (lo resuelve default_root_object)
//   /catalogo/           -> /catalogo/index.html
//   /producto/11282      -> /producto/11282/index.html
//   /datos/buscador.json -> sin cambios (tiene extensión)
//
// Los códigos de producto del ERP son numéricos, así que "tiene un punto en el
// último segmento" es un discriminante seguro para distinguir archivo de ruta.

function handler(event) {
  var request = event.request;
  var uri = request.uri;

  if (uri.endsWith('/')) {
    request.uri = uri + 'index.html';
    return request;
  }

  var ultimoSegmento = uri.substring(uri.lastIndexOf('/') + 1);

  if (ultimoSegmento.indexOf('.') === -1) {
    request.uri = uri + '/index.html';
  }

  return request;
}
