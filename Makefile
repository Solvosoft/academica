# Makefile — Académica (Django 6.0 + djgentelella 0.6)
#
# Inicio rápido con Docker (todo el stack en contenedores):
#   make env build up        # http://localhost:8011  ·  MailHog http://localhost:8026
#   make dsuperuser          # crea el administrador dentro del contenedor
#
# Desarrollo con el código montado en el contenedor (runserver + celery -B):
#   make env build dev       # http://localhost:8000
#
# Desarrollo local (venv en .venv, servicios en Docker):
#   make setup services install run

ROOT_DIR   := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PYTHON_SYS ?= python3.13
VENV       ?= $(ROOT_DIR)/.venv
VENV_BIN    = $(VENV)/bin
# Si existe el venv se usa sin activarlo; si no, el python del PATH.
PYTHON     ?= $(shell test -x $(VENV_BIN)/python && echo $(VENV_BIN)/python || command -v python3)
MANAGE      = cd src && $(PYTHON) manage.py
VERSION    := $(shell sed -n "s/^__version__ = '\(.*\)'/\1/p" src/academica/__init__.py)

COMPOSE    ?= docker compose
DC          = $(COMPOSE) -f docker-compose.yml
DC_DEV      = $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml
WEB         = academica-web
IMAGE       = academica

.DEFAULT_GOAL := help

.PHONY: help
help: ## Muestra esta ayuda
	@echo "Uso: make <target>"
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

##--- Configuración ------------------------------------------------------------

.PHONY: env
env: ## Crea .env y deploy/academica.env desde env.example (no sobrescribe)
	@test -f .env || (cp env.example .env && echo "Creado .env")
	@test -f deploy/academica.env || (cp env.example deploy/academica.env && echo "Creado deploy/academica.env")

.PHONY: setup
setup: ## Crea .venv e instala las dependencias
	@test -x $(VENV_BIN)/python || $(PYTHON_SYS) -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade pip
	$(VENV_BIN)/python -m pip install -r requirements.txt -r requirements-dev.txt

.PHONY: requirements
requirements: ## Reinstala las dependencias en el entorno actual
	$(PYTHON) -m pip install -r requirements.txt

##--- Django (local) -----------------------------------------------------------

.PHONY: check
check: ## Chequeos de Django (incluye migraciones pendientes)
	$(MANAGE) check
	$(MANAGE) makemigrations --check --dry-run

.PHONY: check-deploy
check-deploy: ## Lista de chequeo de despliegue de Django
	cd src && DEBUG=False $(PYTHON) manage.py check --deploy

.PHONY: install
install: ## Migraciones, caché, grupos de permisos y plantillas de correo
	$(MANAGE) academica_install

.PHONY: migrate
migrate: ## Aplica las migraciones
	$(MANAGE) migrate

.PHONY: makemigrations
makemigrations: ## Genera migraciones nuevas
	$(MANAGE) makemigrations

.PHONY: superuser
superuser: ## Crea un superusuario
	$(MANAGE) createsuperuser

.PHONY: run
run: ## Servidor de desarrollo en http://127.0.0.1:8000
	$(MANAGE) runserver

.PHONY: shell
shell: ## Shell de Django
	$(MANAGE) shell

.PHONY: celery
celery: ## Worker de celery con beat embebido (necesita redis)
	cd src && $(PYTHON) -m celery -A academica worker -l info -B \
		--scheduler django_celery_beat.schedulers:DatabaseScheduler

.PHONY: load-templates
load-templates: ## Crea las plantillas de correo que falten (OVERWRITE=1 las reemplaza)
	$(MANAGE) load_email_templates $(if $(OVERWRITE),--overwrite,)

.PHONY: sync-products
sync-products: ## Crea/actualiza los productos de los cursos en el servicio de pagos con tarjeta
	$(MANAGE) sync_gateway_products

.PHONY: send-emails
send-emails: ## Envía los correos encolados de djgentelella
	$(MANAGE) process_notifications

.PHONY: test
test: ## Corre las pruebas sin navegador (TEST=ruta.al.test para una sola)
	$(MANAGE) test --no-input --exclude-tag=selenium $(TEST)

##--- Pruebas de navegación (Selenium) -----------------------------------------
# Corren dentro de una pantalla virtual (xvfb-run) para no abrir ventanas en el
# escritorio. TEST=academica_test.tests.stories.<modulo>[.<Clase>.<prueba>]

SELENIUM_RESULTS ?= $(ROOT_DIR)/selenium-results
XVFB        = xvfb-run --auto-servernum --server-args="-screen 0 1280x720x24"
SELENIUM_TEST = $(PYTHON) manage.py test --settings=academica.test_settings --tag=selenium --no-input
STORIES    ?= academica_test

.PHONY: check-selenium
check-selenium: ## Verifica chromium, chromedriver, xvfb-run, dependencias y PostgreSQL
	$(PYTHON) scripts/check_selenium.py

.PHONY: test-selenium
test-selenium: ## Todas las historias en paralelo, en pantalla virtual (TEST=..., WORKERS=N)
	$(XVFB) sh -c "cd src && $(SELENIUM_TEST) --parallel $(WORKERS) -v 2 $(or $(TEST),$(STORIES))"

.PHONY: test-selenium-single
test-selenium-single: ## Una historia, en serie y en su propia pantalla virtual (TEST=...; GIF=1 genera el GIF)
	@test -n "$(TEST)" || { echo "Falta TEST=ruta.a.la.historia"; exit 2; }
	$(XVFB) sh -c "cd src && GENERATE_SCREENSHOTS=$(if $(GIF),True,False) $(SELENIUM_TEST) -v 2 $(TEST)"

.PHONY: test-selenium-dev
test-selenium-dev: ## Historias en pantalla virtual reutilizando la BD de pruebas (--keepdb)
	$(XVFB) sh -c "cd src && $(SELENIUM_TEST) --keepdb --parallel $(WORKERS) -v 2 $(or $(TEST),$(STORIES))"

.PHONY: test-selenium-screen
test-selenium-screen: ## OJO: abre Chrome en TU pantalla; solo para depurar una historia (TEST=...)
	cd src && $(SELENIUM_TEST) -v 2 $(or $(TEST),$(STORIES))

BITACORA ?= $(SELENIUM_RESULTS)/bitacora_$(shell date +%Y%m%d_%H%M%S).log

.PHONY: test-selenium-bitacora
test-selenium-bitacora: ## Historias en pantalla virtual; guarda el log en selenium-results/ y resume fallos
	@mkdir -p $(SELENIUM_RESULTS)
	-@$(XVFB) sh -c "cd src && $(SELENIUM_TEST) --parallel $(WORKERS) -v 2 $(or $(TEST),$(STORIES))" > $(BITACORA) 2>&1
	@echo "----- resumen -----"
	@grep -E '^(FAIL|ERROR): |^Ran |^OK|^FAILED' $(BITACORA) || echo "sin resultados"
	@echo "Log completo: $(BITACORA)  ·  capturas de fallos: $(SELENIUM_RESULTS)/fallas/"

.PHONY: stories-gif
stories-gif: ## Genera los GIF de todas las historias en selenium-results/gif/ (lento, sin paralelo)
	$(XVFB) sh -c "cd src && GENERATE_SCREENSHOTS=True $(SELENIUM_TEST) -v 2 $(or $(TEST),$(STORIES))"

.PHONY: messages
messages: ## Extrae los textos a traducir (es)
	cd src && $(PYTHON) manage.py makemessages -l es --no-location --ignore "*.min.js"

.PHONY: trans
trans: ## Compila las traducciones
	$(MANAGE) compilemessages -l es

.PHONY: lint
lint: ## Busca errores con pyflakes (requirements-dev.txt)
	find src -name '*.py' -not -path '*/migrations/*' | xargs $(PYTHON) -m pyflakes

.PHONY: clean
clean: ## Borra archivos temporales de Python
	find . -path ./.venv -prune -o -type d -name __pycache__ -exec rm -rf {} +
	find . -path ./.venv -prune -o -type f -name '*.py[co]' -delete

##--- Docker -------------------------------------------------------------------

.PHONY: build
build: ## Construye la imagen academica:<versión> y academica:latest
	docker build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

.PHONY: up
up: env ## Levanta el stack completo en segundo plano
	$(DC) up -d
	@echo "Académica: http://localhost:8011  ·  MailHog: http://localhost:8026"

.PHONY: dev
dev: env ## Levanta el stack con el código montado (runserver en :8000)
	$(DC_DEV) up

.PHONY: services
services: env ## Solo postgres, redis y mailhog (para desarrollo local)
	$(COMPOSE) -f docker-compose.yml -f deploy/docker-compose.services.yml up -d postgresdb redis mail

.PHONY: down
down: ## Detiene el stack (los datos quedan en los volúmenes)
	$(DC) down

.PHONY: logs
logs: ## Sigue los logs del stack
	$(DC) logs -f

.PHONY: ps
ps: ## Estado de los contenedores
	$(DC) ps

.PHONY: dmanage
dmanage: ## manage.py dentro del contenedor web (CMD="showmigrations")
	$(DC) exec $(WEB) runuser -p -u academica -- python manage.py $(CMD)

.PHONY: dshell
dshell: ## Shell de Django dentro del contenedor web
	$(DC) exec $(WEB) runuser -p -u academica -- python manage.py shell

.PHONY: dsuperuser
dsuperuser: ## Crea un superusuario dentro del contenedor web
	$(DC) exec $(WEB) runuser -p -u academica -- python manage.py createsuperuser

.PHONY: dinstall
dinstall: ## Corre academica_install dentro del contenedor web
	$(DC) exec $(WEB) runuser -p -u academica -- python manage.py academica_install

.PHONY: dtest
dtest: ## Corre las pruebas dentro del contenedor web
	$(DC) exec $(WEB) runuser -p -u academica -- python manage.py test --no-input $(TEST)

.PHONY: db-shell
db-shell: ## Consola psql de la base de datos
	$(DC) exec postgresdb sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

.PHONY: db-reset
db-reset: ## BORRA la base de datos y los archivos subidos (pide confirmación)
	@read -p "Esto elimina TODOS los datos de la base y media. ¿Continuar? [y/N]: " ok; \
	if [ "$$ok" = "y" ]; then $(DC) down -v; else echo "Cancelado"; fi
