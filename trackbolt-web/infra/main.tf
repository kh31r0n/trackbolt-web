locals {
  etiquetas = merge(
    {
      Proyecto = "trackbolt"
      Entorno  = "demo"
      Gestion  = "terraform"
    },
    var.etiquetas_extra,
  )

  nombre_bucket = "${var.nombre_proyecto}-${random_id.sufijo.hex}"
}

# El espacio de nombres de S3 es global; el sufijo evita colisiones al recrear.
resource "random_id" "sufijo" {
  byte_length = 4
}

# ---------------------------------------------------------------------------
# Origen: bucket privado. Nada de acceso público directo — todo entra por
# CloudFront, que se identifica con el control de acceso de origen (OAC).
# ---------------------------------------------------------------------------

resource "aws_s3_bucket" "sitio" {
  bucket        = local.nombre_bucket
  force_destroy = true # demo desechable: `terraform destroy` no debe quedarse atascado
}

resource "aws_s3_bucket_public_access_block" "sitio" {
  bucket = aws_s3_bucket.sitio.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "sitio" {
  bucket = aws_s3_bucket.sitio.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sitio" {
  bucket = aws_s3_bucket.sitio.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_cloudfront_origin_access_control" "sitio" {
  name                              = "${local.nombre_bucket}-oac"
  description                       = "Acceso de CloudFront al bucket del sitio de demostración"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

data "aws_iam_policy_document" "sitio" {
  statement {
    sid       = "PermitirLecturaDesdeCloudFront"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.sitio.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    # Solo esta distribución, no cualquier CloudFront de cualquier cuenta.
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.sitio.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "sitio" {
  bucket = aws_s3_bucket.sitio.id
  policy = data.aws_iam_policy_document.sitio.json

  depends_on = [aws_s3_bucket_public_access_block.sitio]
}

# ---------------------------------------------------------------------------
# Reescritura de rutas.
#
# Astro genera URLs de directorio (`/catalogo/` -> `catalogo/index.html`). El
# origen REST de S3 no tiene documento índice por carpeta, así que sin esta
# función toda ruta que no sea la raíz devolvería 403. Se ejecuta en la petición
# del visor, antes de consultar la caché.
# ---------------------------------------------------------------------------

resource "aws_cloudfront_function" "rutas" {
  name    = "${var.nombre_proyecto}-rutas-${random_id.sufijo.hex}"
  runtime = "cloudfront-js-2.0"
  comment = "Añade index.html a las URLs de directorio"
  publish = true
  code    = file("${path.module}/funciones/reescribir-rutas.js")
}

# ---------------------------------------------------------------------------
# Distribución
# ---------------------------------------------------------------------------

data "aws_cloudfront_cache_policy" "optimizada" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_response_headers_policy" "seguridad" {
  name = "Managed-SecurityHeadersPolicy"
}

resource "aws_cloudfront_distribution" "sitio" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = var.comentario_distribucion
  default_root_object = "index.html"
  price_class         = var.clase_precio

  origin {
    origin_id                = "s3-${local.nombre_bucket}"
    domain_name              = aws_s3_bucket.sitio.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.sitio.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-${local.nombre_bucket}"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true

    # La política gestionada respeta el Cache-Control que pone `desplegar.sh`:
    # un año inmutable para /_astro/, un minuto para HTML y JSON.
    cache_policy_id            = data.aws_cloudfront_cache_policy.optimizada.id
    response_headers_policy_id = data.aws_cloudfront_response_headers_policy.seguridad.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.rutas.arn
    }
  }

  # El origen privado responde 403 (no 404) a las claves inexistentes porque la
  # política no concede s3:ListBucket. Se contemplan las dos.
  custom_error_response {
    error_code            = 403
    response_code         = 404
    response_page_path    = "/404.html"
    error_caching_min_ttl = 10
  }

  custom_error_response {
    error_code            = 404
    response_code         = 404
    response_page_path    = "/404.html"
    error_caching_min_ttl = 10
  }

  viewer_certificate {
    # Certificado *.cloudfront.net. Para un dominio propio haría falta un
    # certificado de ACM en us-east-1 y declarar los aliases.
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}
