.PHONY: \
	help \
	ingestion ingestion-docker \
	processing processing-docker \
	processing-all processing-all-docker \
	processing-model processing-model-docker \
	processing-dataset processing-dataset-docker \
	frontend frontend-docker \
	docker-build docker-build-ingestion docker-build-processing docker-build-frontend \

SHELL := /bin/bash

PYTHON ?= python
STREAMLIT ?= streamlit
DOCKER_COMPOSE ?= docker compose
FRONTEND_DIR ?= frontend-web

INGEST ?= all
MODEL ?= bertopic
DATASET ?= abstracts
MODELS ?= lda bertopic top2vec fastopic
DATASETS ?= readmes issues thesis abstracts

help:
	@echo "TFG Topics Make targets"
	@echo ""
	@echo "Local execution"
	@echo "  make ingestion INGEST=\"all\""
	@echo "  make ingestion INGEST=\"issues readmes\""
	@echo "  make processing MODEL=bertopic DATASET=thesis"
	@echo "  make processing-model MODEL=lda"
	@echo "  make processing-dataset DATASET=issues"
	@echo "  make processing-all MODELS=\"lda bertopic\" DATASETS=\"readmes thesis\""
	@echo "  make frontend"
	@echo ""
	@echo "Docker execution"
	@echo "  make ingestion-docker INGEST=\"all\""
	@echo "  make processing-docker MODEL=top2vec DATASET=readmes"
	@echo "  make processing-all-docker"
	@echo "  make frontend-docker"
	@echo ""
	@echo "Docker lifecycle"
	@echo "  make docker-build"

ingestion:
	PYTHONPATH=backend-ingestion/src $(PYTHON) -m ingestion.main --ingest $(INGEST)

ingestion-docker:
	$(DOCKER_COMPOSE) --profile ingestion run --rm ingestion --ingest $(INGEST)

processing:
	PYTHONPATH=backend-processing/src $(PYTHON) -m processing.main --model "$(MODEL)" --dataset "$(DATASET)"

processing-docker:
	$(DOCKER_COMPOSE) --profile processing run --rm processing --model "$(MODEL)" --dataset "$(DATASET)"

processing-model:
	@set -euo pipefail; \
	for dataset in $(DATASETS); do \
		echo ">>> processing model=$(MODEL) dataset=$$dataset"; \
		PYTHONPATH=backend-processing/src $(PYTHON) -m processing.main --model "$(MODEL)" --dataset "$$dataset"; \
	done

processing-model-docker:
	@set -euo pipefail; \
	for dataset in $(DATASETS); do \
		echo ">>> processing model=$(MODEL) dataset=$$dataset"; \
		$(DOCKER_COMPOSE) --profile processing run --rm processing --model "$(MODEL)" --dataset "$$dataset"; \
	done

processing-dataset:
	@set -euo pipefail; \
	for model in $(MODELS); do \
		echo ">>> processing model=$$model dataset=$(DATASET)"; \
		PYTHONPATH=backend-processing/src $(PYTHON) -m processing.main --model "$$model" --dataset "$(DATASET)"; \
	done

processing-dataset-docker:
	@set -euo pipefail; \
	for model in $(MODELS); do \
		echo ">>> processing model=$$model dataset=$(DATASET)"; \
		$(DOCKER_COMPOSE) --profile processing run --rm processing --model "$$model" --dataset "$(DATASET)"; \
	done

processing-all:
	@set -euo pipefail; \
	fail=0; \
	for model in $(MODELS); do \
		for dataset in $(DATASETS); do \
			echo ">>> processing model=$$model dataset=$$dataset"; \
			if ! PYTHONPATH=backend-processing/src $(PYTHON) -m processing.main --model "$$model" --dataset "$$dataset"; then \
				echo "!!! failed model=$$model dataset=$$dataset"; \
				fail=1; \
			fi; \
		done; \
	done; \
	exit $$fail

processing-all-docker:
	@set -euo pipefail; \
	fail=0; \
	for model in $(MODELS); do \
		for dataset in $(DATASETS); do \
			echo ">>> processing model=$$model dataset=$$dataset"; \
			if ! $(DOCKER_COMPOSE) --profile processing run --rm processing --model "$$model" --dataset "$$dataset"; then \
				echo "!!! failed model=$$model dataset=$$dataset"; \
				fail=1; \
			fi; \
		done; \
	done; \
	exit $$fail

frontend:
	cd $(FRONTEND_DIR) && PYTHONPATH=src $(STREAMLIT) run src/webapp/main.py

frontend-docker:
	$(DOCKER_COMPOSE) --profile frontend run --rm frontend


docker-build: docker-build-ingestion docker-build-processing docker-build-frontend

docker-build-ingestion:
	$(DOCKER_COMPOSE) --profile ingestion build

docker-build-processing:
	$(DOCKER_COMPOSE) --profile processing build

docker-build-frontend:
	$(DOCKER_COMPOSE) --profile frontend build
