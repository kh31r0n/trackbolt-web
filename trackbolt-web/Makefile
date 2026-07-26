PY = ../.venv/bin/python

.PHONY: ayuda catalogo test dev build preview limpiar todo

ayuda:
	@echo "make catalogo  - regenera el catálogo desde el Excel del ERP"
	@echo "make test      - ejecuta las pruebas del generador"
	@echo "make dev       - servidor de desarrollo"
	@echo "make build     - sitio estático en dist/"
	@echo "make preview   - sirve dist/ para revisarlo"
	@echo "make todo      - catalogo + test + build"

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
