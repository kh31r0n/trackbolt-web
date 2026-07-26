variable "nombre_proyecto" {
  description = "Prefijo para el nombre del bucket y de los recursos."
  type        = string
  default     = "trackbolt-demo"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,40}[a-z0-9]$", var.nombre_proyecto))
    error_message = "Solo minúsculas, dígitos y guiones: forma parte del nombre del bucket."
  }
}

variable "region" {
  description = "Región del bucket. CloudFront es global, así que solo afecta al origen."
  type        = string
  default     = "us-east-1"
}

variable "perfil_aws" {
  description = "Perfil del archivo de credenciales de AWS. Vacío usa el del entorno."
  type        = string
  default     = ""
}

variable "clase_precio" {
  description = <<-DESC
    Cobertura de puntos de presencia de CloudFront.
    PriceClass_All es la única que incluye Suramérica (Bogotá, São Paulo); con
    PriceClass_200 las visitas colombianas se atienden desde Miami, algo más lento
    pero más barato por GB.
  DESC
  type        = string
  default     = "PriceClass_All"

  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.clase_precio)
    error_message = "Valores admitidos: PriceClass_100, PriceClass_200, PriceClass_All."
  }
}

variable "comentario_distribucion" {
  description = "Texto descriptivo que aparece en la consola de CloudFront."
  type        = string
  default     = "Trackbolt — sitio de demostración"
}

variable "etiquetas_extra" {
  description = "Etiquetas adicionales para todos los recursos."
  type        = map(string)
  default     = {}
}
