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

  default_tags {
    tags = local.etiquetas
  }
}
