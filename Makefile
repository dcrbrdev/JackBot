current_dir = $(notdir $(shell pwd))

config.env:
	cp .env.example .env

##############################
### LOCAL PYTHON COMMANDS ###
#############################
run:
	python -m bot.jack

run.worker:
	python -m sws.client

test:
	pytest

coverage:
	pytest --cov=sws --cov=db --cov=bot
	coverage report
	coverage xml

coverage.codacy:coverage
	python-codacy-coverage -r coverage.xml -t $$CODACY_PROJECT_TOKEN

flake8:
	flake8

pip.install:
	pip install -r requirements-dev.txt

#################################
###### DOCKER DEV COMMANDS ######
#################################
docker.build:
	docker-compose build

docker.logs:
	docker-compose logs -f

docker.up:
	docker-compose up -d

docker.down:
	docker-compose down

docker.bot.bash:
	docker-compose exec bot bash

docker.mongo.bash:
	docker-compose exec mongo bash

docker.test:
	docker-compose run bot pytest

docker.flake8:
	docker-compose run bot flake8

docker.bot.stop:
	docker stop bot

docker.bot.restart: docker.bot.stop docker.up

docker.worker.stop:
	docker stop bot-worker

docker.worker.restart: docker.worker.stop docker.up

docker.volumes.remove: docker.down
	docker volume rm $(current_dir)_mongo_volume

docker.stop.all:
	docker ps | awk '{print $$1}' | grep -v CONTAINER | xargs docker stop

docker.remove.all:
	docker ps -a | awk '{print $$1}' | grep -v CONTAINER | xargs docker rm

#################################
##### DOCKER PROD COMMANDS ######
#################################
docker.prod.build:
	docker-compose -f docker-compose.prod.yml build

docker.prod.logs:
	docker-compose -f docker-compose.prod.yml logs -f

docker.prod.up:
	docker-compose -f docker-compose.prod.yml up -d

docker.prod.down:
	docker-compose -f docker-compose.prod.yml down

docker.prod.bot.bash:
	docker-compose -f docker-compose.prod.yml exec bot bash

docker.prod.mongo.bash:
	docker-compose -f docker-compose.prod.yml exec mongo bash

#################################
###### DOCKER ARM COMMANDS ######
#################################
docker.arm.build:
	docker-compose -f docker-compose.arm.yml build

docker.arm.logs:
	docker-compose -f docker-compose.arm.yml logs -f

docker.arm.up:
	docker-compose -f docker-compose.arm.yml up -d

docker.arm.down:
	docker-compose -f docker-compose.arm.yml down

docker.arm.bot.bash:
	docker-compose -f docker-compose.arm.yml exec bot bash

docker.arm.mongo.bash:
	docker-compose -f docker-compose.arm.yml exec mongo bash
