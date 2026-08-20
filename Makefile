include .env

.DEFAULT_GOAL := help

.PHONY: help check-traefik image rebuild up shell rootshell logs

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

check-traefik:
ifeq (,$(shell docker ps -f name=^traefik$$ -q))
	$(error docker container traefik is not running)
endif

.env:
	$(error file .env is missing, see .env.sample)

image: ## (Re)build the docker image without cache
	@echo "(Re)building docker image"
	docker compose build --no-cache --pull app

rebuild: ## Rebuild the docker image using cache
	@echo "Rebuilding docker image"
	docker compose build app

dev: prod ## Recreate and start the app container in development mode
	docker compose up -d --force-recreate --remove-orphans app

prod: check-traefik ## Recreate and start the app container
	docker compose up -d --pull always --force-recreate --remove-orphans app

shell: ## Open a shell inside the app container
	docker compose exec app sh

rootshell: ## Open a root shell inside the app container
	docker compose exec --user root app sh

logs: ## Tail logs from all containers
	docker compose logs -f
