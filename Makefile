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
	sudo docker-compose build

docker.logs:
	sudo docker-compose logs -f

docker.up:
	sudo docker-compose up -d

docker.down:
	sudo docker-compose down

docker.bot.bash:
	sudo docker-compose exec bot bash

docker.mongo.bash:
	sudo docker-compose exec mongo bash

docker.test:
	sudo docker-compose run bot pytest

docker.flake8:
	sudo docker-compose run bot flake8

docker.bot.stop:
	sudo docker stop bot

docker.bot.restart: docker.bot.stop docker.up

docker.session_watcher.stop:
	sudo docker stop session-watcher

docker.session_watcher.restart: docker.session_watcher.stop docker.up

docker.ticket_watcher.stop:
	sudo docker stop ticket-watcher

docker.ticket_watcher.restart: docker.ticket_watcher.stop docker.up

docker.volumes.remove: docker.down
	sudo docker volume rm $(current_dir)_mongo_volume

docker.stop.all:
	sudo docker ps | awk '{print $$1}' | grep -v CONTAINER | xargs sudo docker stop

docker.remove.all:
	sudo docker ps -a | awk '{print $$1}' | grep -v CONTAINER | xargs sudo docker rm

#################################
##### DOCKER PROD COMMANDS ######
#################################
docker.prod.build:
	sudo docker-compose -f docker-compose.prod.yml build

docker.prod.logs:
	sudo docker-compose -f docker-compose.prod.yml logs -f

docker.prod.up:
	sudo docker-compose -f docker-compose.prod.yml up -d

docker.prod.down:
	sudo docker-compose -f docker-compose.prod.yml down

docker.prod.bot.bash:
	sudo docker-compose -f docker-compose.prod.yml exec bot bash

docker.prod.mongo.bash:
	sudo docker-compose -f docker-compose.prod.yml exec mongo bash

#################################
###### DOCKER ARM COMMANDS ######
#################################
docker.arm.build:
	sudo docker-compose -f docker-compose.arm.yml build

docker.arm.logs:
	sudo docker-compose -f docker-compose.arm.yml logs -f

docker.arm.up:
	sudo docker-compose -f docker-compose.arm.yml up -d

docker.arm.down:
	sudo docker-compose -f docker-compose.arm.yml down

docker.arm.bot.bash:
	sudo docker-compose -f docker-compose.arm.yml exec bot bash

docker.arm.mongo.bash:
	sudo docker-compose -f docker-compose.arm.yml exec mongo bash
