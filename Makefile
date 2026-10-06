.DEFAULT_GOAL := help

ROOT := $(CURDIR)
ODOO_DIR ?= $(ROOT)/odoo19
PYTHON := $(ODOO_DIR)/.venv/bin/python
ODOO_BIN := $(ODOO_DIR)/odoo-bin

DATA_DIR ?= /sgoinfre/goinfre/Perso/rtijani/odoo_data
DB_NAME ?= produits_tendance_dev
DB_USER ?= odoo
DB_PASSWORD ?= odoo
DB_PORT ?= 5432
DB_CONTAINER ?= produits-postgres
DB_VOLUME := produits_postgres_data
DB_IMAGE := postgres:14

ODOO_ARGS = \
	--addons-path=$(ODOO_DIR)/addons,$(ROOT) \
	--data-dir=$(DATA_DIR) \
	--db_host=localhost \
	--db_port=$(DB_PORT) \
	--db_user=$(DB_USER) \
	--db_password=$(DB_PASSWORD) \
	--http-interface=127.0.0.1 \
	-d $(DB_NAME)

.PHONY: help docker-start db-start db-check start upgrade shell status db-stop

help:
	@echo "make start     - Start PostgreSQL and run Odoo"
	@echo "make upgrade   - Upgrade produits_tendance"
	@echo "make shell     - Open the Odoo Python shell"
	@echo "make db-check  - Check PostgreSQL readiness"
	@echo "make status    - Show database container status"
	@echo "make db-stop   - Stop the project database"

.PHONY: db-create install

db-create: docker-start
	docker volume create $(DB_VOLUME)
	docker run -d \
		--name $(DB_CONTAINER) \
		--restart unless-stopped \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-e POSTGRES_DB=$(DB_NAME) \
		-p 127.0.0.1:$(DB_PORT):5432 \
		-v $(DB_VOLUME):/var/lib/postgresql/data \
		$(DB_IMAGE)

install: db-start
	$(PYTHON) $(ODOO_BIN) $(ODOO_ARGS) \
		-i produits_tendance --stop-after-init --no-http

docker-start:
	systemctl --user start docker

db-start: docker-start
	docker start $(DB_CONTAINER)
	@attempt=0; \
	until docker exec $(DB_CONTAINER) pg_isready \
		-U $(DB_USER) -d $(DB_NAME); do \
		attempt=$$((attempt + 1)); \
		if [ $$attempt -ge 15 ]; then \
			echo "PostgreSQL did not become ready."; \
			exit 1; \
		fi; \
		sleep 2; \
	done

db-check:
	docker exec $(DB_CONTAINER) pg_isready \
		-U $(DB_USER) -d $(DB_NAME)

start: db-start
	$(PYTHON) $(ODOO_BIN) $(ODOO_ARGS)

upgrade: db-start
	$(PYTHON) $(ODOO_BIN) $(ODOO_ARGS) \
		-u produits_tendance --stop-after-init --no-http

shell: db-start
	$(PYTHON) $(ODOO_BIN) shell $(ODOO_ARGS) --no-http

status:
	docker ps -a --filter name=$(DB_CONTAINER)

db-stop:
	docker stop $(DB_CONTAINER)