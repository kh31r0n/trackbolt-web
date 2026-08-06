# Copiar a terraform.tfvars y ajustar. Todos los valores tienen predeterminado,
# así que el archivo es opcional.

# nombre_proyecto = "trackbolt-demo"
# region          = "us-east-1"
# perfil_aws      = ""            # vacío usa las credenciales del entorno
# clase_precio    = "PriceClass_All"

# La cuenta contra la que se permite operar. Su predeterminado ya apunta a la
# cuenta real; sobrescribirlo aquí solo tiene sentido al mover el proyecto de
# cuenta, y entonces conviene cambiar también el predeterminado en variables.tf.
# cuenta_aws = "006392690655"

# demo (bucket con force_destroy, banner y robots Disallow) o produccion.
# entorno = "demo"

# Poner en false para dejar /interno/ fuera del bucket. Ver el README antes:
# la exposición actual es una decisión consciente del cliente.
# publicar_interno = true

# etiquetas_extra = {
#   Cliente = "trackbolt"
#   Costo   = "preventa"
# }
