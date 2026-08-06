#!/usr/bin/env bash
#
# Compila el sitio y lo publica en el bucket de la demo.
#
#   ./infra/desplegar.sh                 compila y sube
#   ./infra/desplegar.sh --catalogo      regenera antes el catálogo desde el Excel
#   ./infra/desplegar.sh --sin-invalidar no invalida la caché de CloudFront
#   ./infra/desplegar.sh --esperar       espera a que termine la invalidación
#
# Requiere que `terraform apply` ya haya creado la infraestructura: la URL del
# sitio se lee de las salidas de Terraform y se le pasa a Astro, para que el
# sitemap y las canónicas de la demo no apunten a producción.

set -euo pipefail

INFRA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$INFRA")"

REGENERAR_CATALOGO=0
INVALIDAR=1
ESPERAR=0

for argumento in "$@"; do
  case "$argumento" in
    --catalogo)      REGENERAR_CATALOGO=1 ;;
    --sin-invalidar) INVALIDAR=0 ;;
    --esperar)       ESPERAR=1 ;;
    -h|--help)       sed -n '2,12p' "${BASH_SOURCE[0]}" | cut -c3-; exit 0 ;;
    *)               echo "Argumento desconocido: $argumento" >&2; exit 2 ;;
  esac
done

paso() { printf '\n\033[1;31m▸\033[0m \033[1m%s\033[0m\n' "$1"; }
aviso() { printf '  %s\n' "$1"; }
morir() { printf '\n\033[1;31mError:\033[0m %s\n' "$1" >&2; exit 1; }

for binario in terraform aws npm; do
  command -v "$binario" >/dev/null 2>&1 || morir "falta '$binario' en el PATH."
done

# ---------------------------------------------------------------------------
# 1. Salidas de Terraform
# ---------------------------------------------------------------------------

paso "Leyendo la infraestructura"

salida() {
  terraform -chdir="$INFRA" output -raw "$1" 2>/dev/null \
    || morir "no se pudo leer la salida '$1'. ¿Ejecutaste 'terraform -chdir=infra apply'?"
}

BUCKET="$(salida bucket)"
DISTRIBUCION="$(salida distribucion_id)"
URL_SITIO="$(salida url_sitio)"
REGION="$(salida region)"
ENTORNO="$(salida entorno)"
CUENTA_ESPERADA="$(salida cuenta)"
PUBLICAR_INTERNO="$(salida publicar_interno)"

aviso "entorno:      $ENTORNO"
aviso "bucket:       $BUCKET ($REGION)"
aviso "distribución: $DISTRIBUCION"
aviso "url:          $URL_SITIO"

# Terraform se protege con allowed_account_ids, pero aquí se llama a la CLI
# directamente: sin esta comprobación, unas credenciales de otra cuenta darían
# un 403 a media subida, o peor, subirían a un bucket homónimo ajeno.
CUENTA_ACTUAL="$(aws sts get-caller-identity --query Account --output text 2>/dev/null)" \
  || morir "las credenciales de AWS no son válidas. Revisa AWS_PROFILE o ejecuta 'aws configure'."

[[ "$CUENTA_ACTUAL" == "$CUENTA_ESPERADA" ]] \
  || morir "credenciales de la cuenta $CUENTA_ACTUAL, pero la infraestructura vive en $CUENTA_ESPERADA. Revisa AWS_PROFILE."

aviso "cuenta:       $CUENTA_ACTUAL"

# ---------------------------------------------------------------------------
# 2. Catálogo (opcional) y compilación
# ---------------------------------------------------------------------------

if [[ $REGENERAR_CATALOGO -eq 1 ]]; then
  paso "Regenerando el catálogo desde el Excel"
  PY="$RAIZ/../.venv/bin/python"
  [[ -x "$PY" ]] || morir "no existe el entorno virtual en $PY. Omite --catalogo para usar el JSON ya generado."
  (cd "$RAIZ" && "$PY" scripts/build_catalogo.py)
fi

paso "Compilando el sitio"

[[ -d "$RAIZ/node_modules" ]] || (cd "$RAIZ" && npm ci)

rm -rf "$RAIZ/dist"
(
  cd "$RAIZ"
  if [[ "$ENTORNO" == "demo" ]]; then
    TRACKBOLT_DEMO=1 TRACKBOLT_URL="$URL_SITIO" npm run build
  else
    TRACKBOLT_URL="$URL_SITIO" npm run build
  fi
)

[[ -f "$RAIZ/dist/index.html" ]] || morir "la compilación no produjo dist/index.html."

# La demo no debe indexarse ni competir con trackbolt.co en los buscadores.
# El robots.txt de public/ anuncia el sitemap de producción, así que se sustituye.
# En producción se deja el de public/ tal cual.
if [[ "$ENTORNO" == "demo" ]]; then
  cat > "$RAIZ/dist/robots.txt" <<ROBOTS
# Sitio de demostración. No indexar.
User-agent: *
Disallow: /
ROBOTS
fi

aviso "$(find "$RAIZ/dist" -type f | wc -l) archivos, $(du -sh "$RAIZ/dist" | cut -f1)"

# ---------------------------------------------------------------------------
# 3. Sincronización
#
# Dos pasadas porque el Cache-Control difiere. Cada una lleva su propio --delete
# acotado por los mismos filtros, de modo que ninguna borra los archivos de la otra.
# ---------------------------------------------------------------------------

paso "Subiendo a S3"

# Exclusiones comunes a las dos pasadas. Tienen que ser idénticas: cada --delete
# está acotado por los filtros de su pasada, así que una exclusión presente solo
# en una haría que la otra borrase lo que la primera acaba de subir.
COMUNES=()
if [[ "$PUBLICAR_INTERNO" != "true" ]]; then
  aviso "/interno/ excluido del despliegue (publicar_interno = false)"
  COMUNES+=(--exclude "interno/*" --exclude "datos/interno.json")
fi

aviso "activos con huella (/_astro/) — caché de un año"
aws s3 sync "$RAIZ/dist/" "s3://$BUCKET/" \
  --region "$REGION" \
  --delete \
  --only-show-errors \
  "${COMUNES[@]}" \
  --exclude "*" --include "_astro/*" \
  --cache-control "public, max-age=31536000, immutable"

aviso "HTML, JSON e imágenes — caché de un minuto, revalidando (2.800 archivos, puede tardar)"
aws s3 sync "$RAIZ/dist/" "s3://$BUCKET/" \
  --region "$REGION" \
  --delete \
  --only-show-errors \
  "${COMUNES[@]}" \
  --exclude "_astro/*" \
  --cache-control "public, max-age=60, must-revalidate"

# ---------------------------------------------------------------------------
# 4. Invalidación
# ---------------------------------------------------------------------------

if [[ $INVALIDAR -eq 1 ]]; then
  paso "Invalidando la caché de CloudFront"
  INVALIDACION="$(aws cloudfront create-invalidation \
    --distribution-id "$DISTRIBUCION" \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)"
  aviso "invalidación $INVALIDACION"

  if [[ $ESPERAR -eq 1 ]]; then
    aviso "esperando a que se propague (puede tardar unos minutos)…"
    aws cloudfront wait invalidation-completed \
      --distribution-id "$DISTRIBUCION" \
      --id "$INVALIDACION"
    aviso "propagada"
  fi
fi

paso "Listo"
printf '  \033[1m%s\033[0m\n\n' "$URL_SITIO"
