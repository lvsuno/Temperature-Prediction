# LOCAL_TAG:=$(shell date "+%Y-%m-%d-%H-%M")
LOCAL_TAG:=latest
TERRAFORM_FOLDER =infrastructure/mage/aws

include .env

LOCAL_IMAGE_NAME:=$(DOCKER_USERNAME)/mage-ochestration:${APP_VERSION}

# test:
# 	pytest tests/

quality-checks:
	pylint --recursive=y .
	black .
	isort .

build: quality-checks check-docker-env test
	docker build -t ${LOCAL_IMAGE_NAME} . --platform=linux/amd64

integration_test: build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash integration-tests/run.sh

publish-docker: integration_test
#   LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash scripts/publish.sh
	cat $(DOCKER_PASSWORD_FILE) | docker login --username "${DOCKER_USERNAME}" --password-stdin
	docker push ${LOCAL_IMAGE_NAME}

run-local:
	docker-compose up

setup:
	pipenv install --dev
	pre-commit install


init:
	terraform -chdir=$(TERRAFORM_FOLDER) init -reconfigure

plan: check-aws-env
	terraform -chdir=$(TERRAFORM_FOLDER) plan

apply: check-aws-env plan
	terraform -chdir=$(TERRAFORM_FOLDER) apply -var 'access_key'=$(AWS_ACCESS_KEY_ID) -var 'secret_key'=$(AWS_SECRET_ACCESS_KEY) -auto-approve

create_infra: init apply

deploy: check-docker-env check-aws-env publish-docker
	terraform -chdir=$(TERRAFORM_FOLDER) apply -var 'flask_app_image'=$(LOCAL_IMAGE_NAME) -auto-approve

scratch_deploy: check-docker-env check-aws-env publish-docker init
	terraform -chdir=$(TERRAFORM_FOLDER) apply -var 'flask_app_image'=$(LOCAL_IMAGE_NAME) -var 'access_key'=$(AWS_ACCESS_KEY_ID) -var 'secret_key'=$(AWS_SECRET_ACCESS_KEY) -auto-approve


check-docker-env:
	ifndef DOCKER_USERNAME
	    $(error DOCKER_USERNAME is not set)
	endif

	ifndef DOCKER_PASSWORD
	    $(error DOCKER_PASSWORD is not set)
	endif

check-aws-env:
	ifndef AWS_ACCESS_KEY_ID
	    $(error AWS_ACCESS_KEY_ID is not set)
	endif

	ifndef AWS_SECRET_ACCESS_KEY
	    $(error AWS_SECRET_ACCESS_KEY is not set)
	endif

publish-docker: check-docker-env build
	docker login --username "${DOCKER_USERNAME}" --password "${DOCKER_PASSWORD}
	docker push ${LOCAL_IMAGE_NAME}:${LOCAL_TAG}

publish: integration_test
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash scripts/publish.sh

setup:
	pipenv install --dev
	pre-commit install
