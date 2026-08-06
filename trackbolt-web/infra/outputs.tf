output "url_sitio" {
  description = "URL de la demo. Es la que se le pasa al cliente."
  value       = "https://${aws_cloudfront_distribution.sitio.domain_name}"
}

output "bucket" {
  description = "Nombre del bucket de origen."
  value       = aws_s3_bucket.sitio.bucket
}

output "distribucion_id" {
  description = "ID de la distribución, necesario para invalidar la caché."
  value       = aws_cloudfront_distribution.sitio.id
}

output "region" {
  description = "Región del bucket."
  value       = var.region
}

output "cuenta" {
  description = "Cuenta de AWS donde vive la infraestructura. `desplegar.sh` la contrasta con sus credenciales."
  value       = data.aws_caller_identity.actual.account_id
}

output "entorno" {
  description = "demo o produccion."
  value       = var.entorno
}

output "publicar_interno" {
  description = "Si el despliegue debe subir /interno/ al bucket."
  value       = var.publicar_interno
}
