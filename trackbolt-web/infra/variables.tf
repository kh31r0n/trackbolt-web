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

variable "cuenta_aws" {
  description = <<-DESC
    ID de la cuenta de AWS donde vive esta infraestructura. Terraform aborta si
    las credenciales apuntan a otra. Va versionado a propósito: `*.tfvars` está
    en .gitignore, así que un valor puesto ahí no sobrevive a un clon nuevo.
  DESC
  type        = string
  default     = "006392690655"

  validation {
    condition     = can(regex("^[0-9]{12}$", var.cuenta_aws))
    error_message = "El ID de cuenta son 12 dígitos."
  }
}

variable "entorno" {
  description = <<-DESC
    `demo` es desechable: el bucket lleva force_destroy para que `destroy` no se
    atasque. `produccion` lo quita, de modo que un destroy accidental no se lleve
    por delante el contenido.
  DESC
  type        = string
  default     = "demo"

  validation {
    condition     = contains(["demo", "produccion"], var.entorno)
    error_message = "Valores admitidos: demo, produccion."
  }
}

variable "publicar_interno" {
  description = <<-DESC
    Si se sube `/interno/` (costos, cantidades y los cuatro niveles de precio) al
    bucket. La URL de CloudFront es pública, así que `true` expone esa página a
    cualquiera que la tenga. Es la decisión que tomó el cliente para la demo; ver
    el README antes de cambiarla. Lo lee `desplegar.sh`, no Terraform.
  DESC
  type        = bool
  default     = true
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
  description = <<-DESC
    Texto descriptivo que aparece en la consola de CloudFront. Vacío lo deriva
    del entorno (los predeterminados de una variable no pueden leer otra).
  DESC
  type        = string
  default     = ""
}

variable "etiquetas_extra" {
  description = "Etiquetas adicionales para todos los recursos."
  type        = map(string)
  default     = {}
}
