# ---------------------------------------------------------------------------
# Usuario de despliegue.
#
# Credenciales para que un tercero pueda actualizar el portal con
# `desplegar.sh` sin darle acceso a nada más de la cuenta: puede escribir en
# este bucket e invalidar esta distribución, y se acabó. No puede borrar el
# bucket, ni modificar la distribución, ni ver otros recursos.
#
# Para revocar el acceso: `crear_usuario_despliegue = false` y aplicar. Para
# rotar la clave: `terraform taint aws_iam_access_key.despliegue` y aplicar.
# ---------------------------------------------------------------------------

resource "aws_iam_user" "despliegue" {
  count = var.crear_usuario_despliegue ? 1 : 0

  name = "${var.nombre_proyecto}-despliegue"

  # Si se elimina el usuario, que se lleve por delante sus claves.
  force_destroy = true
}

data "aws_iam_policy_document" "despliegue" {
  # `aws s3 sync` necesita listar para saber qué subir y qué borrar con --delete.
  statement {
    sid       = "ListarElBucketDelSitio"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.sitio.arn]
  }

  # Get para comparar tamaños y fechas, Put para subir con su Cache-Control,
  # Delete para lo que ya no existe en dist/, Abort para limpiar una subida
  # multiparte interrumpida.
  statement {
    sid = "EscribirElContenidoDelSitio"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:AbortMultipartUpload",
    ]

    resources = ["${aws_s3_bucket.sitio.arn}/*"]
  }

  # CreateInvalidation para el despliegue; GetInvalidation para `--esperar`.
  statement {
    sid = "InvalidarLaCache"

    actions = [
      "cloudfront:CreateInvalidation",
      "cloudfront:GetInvalidation",
    ]

    resources = [aws_cloudfront_distribution.sitio.arn]
  }
}

resource "aws_iam_user_policy" "despliegue" {
  count = var.crear_usuario_despliegue ? 1 : 0

  name   = "publicar-sitio"
  user   = aws_iam_user.despliegue[0].name
  policy = data.aws_iam_policy_document.despliegue.json
}

resource "aws_iam_access_key" "despliegue" {
  count = var.crear_usuario_despliegue ? 1 : 0

  user = aws_iam_user.despliegue[0].name
}
