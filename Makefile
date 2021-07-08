# set default shell
GROUP_ID = $(shell id -g)
USER_ID = $(shell id -u)

# default shell options
.SILENT: ;
default: help;   # default target

fixtures: ## Setup everything
	$(MAKE) rm
	docker-compose build
	$(MAKE) up
.PHONY: fixtures

vendor: ## install repositories and vendors
	docker-compose run --rm mlflow poetry install --remove-untracked
	# sudo chmod -R 777 .cache
.PHONY: vendor

up: ## docker-compose up in daemon mode + process status
	docker-compose up -d --remove-orphans
	$(MAKE) ps
.PHONY: up

ps: ## docker-compose process status
	docker-compose ps
.PHONY: ps

rm: ## stop and delete containers but leave network and volumes
	docker-compose rm -f -v -s
.PHONY: rm

install: rm vendor up ## Do install
.PHONY: install

all: ## Do all
	$(MAKE) rm
	docker-compose build
	$(MAKE) vendor
	$(MAKE) up
.PHONY: all

services: ## List all possible services
	docker-compose config --service
.PHONY: services

_ubuntu:
	docker pull ubuntu
.PHONY: _ubuntu

docker_make: ## Running command inside docker
	 @:$(call check_defined, cmd, command)
	 echo "Running command inside docker, with home dir $$(echo ~): ${cmd}"
	 docker run -it -v $$(pwd):/work/ -v $$(echo ~):/root/ -w /work ubuntu ${cmd}
.PHONY: docker_make

chown: _ubuntu ## Own your dir ! Don't let root get you !
	$(MAKE) docker_make cmd="chown -R ${USER_ID}:${GROUP_ID} ."
	$(MAKE) docker_make cmd="chmod -R 777 ."
.PHONY: chown

help: ## display help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help