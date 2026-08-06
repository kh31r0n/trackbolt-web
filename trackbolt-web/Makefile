PY = ../.venv/bin/python

TF = terraform -chdir=infra

.PHONY: ayuda catalogo test dev build preview limpiar todo \
        infra-init infra-plan infra-aplicar infra-destruir desplegar demo

ayuda:
	@echo "make catalogo      - regenera el catálogo desde el Excel del ERP"
	@echo "make test          - ejecuta las pruebas del generador"
	@echo "make dev           - servidor de desarrollo"
	@echo "make build         - sitio estático en dist/"
	@echo "make preview       - sirve dist/ para revisarlo"
	@echo "make todo          - catalogo + test + build"
	@echo ""
	@echo "make demo          - compila con el banner de demo, sin subir nada"
	@echo "make infra-init    - inicializa Terraform (una sola vez)"
	@echo "make infra-plan    - muestra qué se va a crear en AWS"
	@echo "make infra-aplicar - crea el bucket y la distribución de CloudFront"
	@echo "make desplegar     - compila y publica en el bucket de la demo"
	@echo "make infra-destruir- borra toda la infraestructura de la demo"
	@echo ""
	@echo "AWS: todo va a la cuenta 006392690655 en us-east-1. Terraform y"
	@echo "desplegar.sh abortan si las credenciales son de otra cuenta."

catalogo:
	$(PY) scripts/build_catalogo.py

test:
	$(PY) -m pytest scripts/tests -q

dev:
	npm run dev

build:
	npm run build

preview:
	npm run preview

limpiar:
	rm -rf dist .astro

todo: catalogo test build

# --- Demostración en AWS --------------------------------------------------

demo:
	TRACKBOLT_DEMO=1 npm run build

infra-init:
	$(TF) init

infra-plan:
	$(TF) plan

infra-aplicar:
	$(TF) apply

infra-destruir:
	$(TF) destroy

desplegar:
	./infra/desplegar.sh
