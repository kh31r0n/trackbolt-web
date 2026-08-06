terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40, < 7.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Estado local: un solo operador, demo desechable. Si esto pasa a producción,
  # migrar a un backend S3 con bloqueo antes de que lo toque un segundo equipo.
}

provider "aws" {
  region  = var.region
  profile = var.perfil_aws != "" ? var.perfil_aws : null

  # Guardia de cuenta. El nombre del bucket es único global, así que unas
  # credenciales de otra cuenta no dan "no existe" sino 403, y CloudFront
  # simplemente no encuentra nada: el refresco borra los recursos del plan y
  # Terraform propone recrearlo todo por duplicado en la cuenta equivocada.
  # Esto aborta antes de leer nada, sea cual sea el perfil o AWS_PROFILE.
  allowed_account_ids = [var.cuenta_aws]

  default_tags {
    tags = local.etiquetas
  }
}
