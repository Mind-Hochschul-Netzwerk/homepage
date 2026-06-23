include .env

check-traefik:
ifeq (,$(shell docker ps -f name=^traefik$$ -q))
	$(error docker container traefik is not running)
endif

.env:
	$(error file .env is missing, see .env.sample)

image:
	@echo "(Re)building docker image"
	docker build --no-cache -t ghcr.io/mind-hochschul-netzwerk/$(SERVICENAME):latest .

rebuild:
	@echo "Rebuilding docker image"
	docker build -t ghcr.io/mind-hochschul-netzwerk/$(SERVICENAME):latest .

up: check-traefik
	docker compose up -d --pull always --force-recreate --remove-orphans app

shell:
	docker compose exec app sh

rootshell:
	docker compose exec --user root app sh

logs:
	docker compose logs -f
