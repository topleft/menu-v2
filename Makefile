.PHONY: all clean build test deploy local

# Variables
STACK_NAME ?= recipe-api
AWS_REGION ?= us-east-1
PYTHON_VERSION ?= 3.12
AWS_PROFILE ?= cicd

all: clean build test

clean:
	rm -rf .aws-sam
	rm -rf python
	rm -f python.zip
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .coverage

build: clean
	poetry run ./build.sh

	# Build SAM application
	sam build --profile $(AWS_PROFILE)

test:
	# Run Python tests
	poetry run pytest

deploy:
	sam deploy \
		--stack-name $(STACK_NAME) \
		--region $(AWS_REGION) \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--profile $(AWS_PROFILE) \
		--no-confirm-changeset

local:
	sam local start-api \
		--port 3000 \
		--env-vars env.json \
		--profile $(AWS_PROFILE)

# Development commands
install:
	poetry env use python$(PYTHON_VERSION)
	poetry env activate
	poetry install

lint:
	poetry run flake8 src
	poetry run black --check src
	poetry run mypy src

format:
	poetry run black src
	poetry run isort src

# Docker commands
docker-build:
	docker build -t recipe-api .

docker-run:
	docker run -p 3000:3000 \
		-e DYNAMODB_TABLE=recipes \
		-e S3_BUCKET=recipe-images \
		recipe-api

# Utility commands
logs:
	sam logs -n RecipeAPI --stack-name $(STACK_NAME) --tail

invoke:
	sam local invoke RecipeAPI -e events/event.json

package:
	sam package \
		--template-file template.yaml \
		--output-template-file packaged.yaml \
		--s3-bucket $(shell aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query 'Stacks[0].Outputs[?OutputKey==`DeploymentBucketName`].OutputValue' --output text)

# Poetry commands
poetry-install:
	curl -sSL https://install.python-poetry.org | python3 -

poetry-update:
	poetry update

poetry-export:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# Help command
help:
	@echo "Available commands:"
	@echo "  make all            - Clean, build, and test"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make build          - Build the application"
	@echo "  make test           - Run tests"
	@echo "  make deploy         - Deploy to AWS"
	@echo "  make local          - Run locally"
	@echo "  make install        - Install dependencies"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make logs           - View CloudWatch logs"
	@echo "  make invoke         - Invoke function locally"
	@echo "  make package        - Package for deployment"
	@echo "  make poetry-install - Install Poetry"
	@echo "  make poetry-update  - Update dependencies"
	@echo "  make poetry-export  - Export dependencies to requirements.txt"
	@echo "  make help           - Show this help message"
