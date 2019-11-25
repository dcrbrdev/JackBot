current_dir = $(notdir $(shell pwd))

config.env:
	cp .env.example .env

##############################
### LOCAL PYTHON COMMANDS ###
#############################
run:
	python run.py

test:
	pytest

coverage:
	pytest --cov=commands
	pytest --cov=core --cov-append
	pytest --cov=db --cov-append
	pytest --cov=bot --cov-append
	coverage report
	coverage xml

coverage.codacy: coverage
	python-codacy-coverage -r coverage.xml -t $$CODACY_PROJECT_TOKEN

flake8:
	flake8

pip.install:
	pip install -r requirements-dev.txt

##############################
###### DOCKER COMMANDS ######
#############################
docker.build:
	docker-compose build

docker.logs:
	docker-compose logs -f

docker.up:
	docker-compose up -d

docker.down:
	docker-compose down

docker.bash:
	docker-compose run bot bash

docker.test:
	docker-compose run bot pytest

docker.flake8:
	docker-compose run bot flake8

docker.bot.stop:
	docker stop bot

docker.bot.restart: docker.bot.stop docker.up

docker.volumes.remove: docker.down
	docker volume rm $(current_dir)_mongo_volume