.PHONY: \
	help \
	ingestion \
	processing \
	frontend \
	print-mode \
	start \
	ingest-all \
	process-all \
	pipeline \
	pull \
	docker-build docker-build-ingestion docker-build-processing docker-build-frontend

SHELL := /bin/bash

PYTHON ?= python
STREAMLIT ?= streamlit
DOCKER_COMPOSE ?= docker compose
DOCKER_COMPOSE_RELEASE ?= $(DOCKER_COMPOSE) -f docker-compose.release.yml
FRONTEND_DIR ?= frontend-web

INGEST ?= all
MODELS ?= bertopic
DATASETS ?= abstracts

MODE ?= release

help:
	@echo "TFG Topics Make targets"
	@echo ""
	@echo "Usage examples (Simplified):"
	@echo "  make start                                (Runs frontend via Docker release by default)"
	@echo "  make ingest-all                           (Runs ingestion via Docker release by default)"
	@echo "  make process-all                          (Runs all models via Docker release by default)"
	@echo "  make pipeline                             (Runs ingest-all, process-all, and start sequentially)"
	@echo "  make pull                                 (Pulls the latest pre-built Docker release images)"
	@echo ""
	@echo "Advanced usage examples:"
	@echo "  make frontend                             (Runs frontend using pre-built release images)"
	@echo "  make ingestion INGEST=\"all\" MODE=local  (Runs ingestion using local Python env)"
	@echo "  make processing MODELS=\"lda bertopic\"   (Runs processing using release images)"
	@echo ""
	@echo "Variables:"
	@echo "  MODE: Execution mode. Options: 'release' (default), 'docker' (local build), 'local' (python)."
	@echo "  INGEST: 'all', 'issues', 'readmes', 'thesis', 'abstracts'."
	@echo "  MODELS: space-separated list of models (e.g. 'lda bertopic top2vec fastopic')."
	@echo "  DATASETS: space-separated list of datasets (e.g. 'readmes issues thesis abstracts')."
	@echo ""
	@echo "Docker lifecycle (for MODE=docker):"
	@echo "  make docker-build"

print-mode:
	@echo "------------------------------------------------------------"
	@echo "🚀 RUNNING IN '$(MODE)' MODE"
ifeq ($(MODE),release)
	@echo "📦 Using pre-built Docker release images. No local setup needed."
	@echo "💡 Tip: To run with local Python env, append 'MODE=local'"
else ifeq ($(MODE),docker)
	@echo "🐳 Using locally built Docker images."
else ifeq ($(MODE),local)
	@echo "🐍 Using local Python environment."
endif
	@echo "------------------------------------------------------------"

ingestion: print-mode
ifeq ($(MODE),release)
	$(DOCKER_COMPOSE_RELEASE) --profile ingestion run --rm ingestion --ingest $(INGEST)
else ifeq ($(MODE),docker)
	$(DOCKER_COMPOSE) --profile ingestion run --rm ingestion --ingest $(INGEST)
else ifeq ($(MODE),local)
	PYTHONPATH=backend-ingestion/src $(PYTHON) -m ingestion.main --ingest $(INGEST)
else
	@echo "Invalid MODE: $(MODE). Use release, docker, or local." && exit 1
endif

processing: print-mode
	@set -euo pipefail; \
	fail=0; \
	for model in $(MODELS); do \
		for dataset in $(DATASETS); do \
			echo ">>> processing model=$$model dataset=$$dataset (mode: $(MODE))"; \
			if [ "$(MODE)" = "release" ]; then \
				$(DOCKER_COMPOSE_RELEASE) --profile processing run --rm processing --model "$$model" --dataset "$$dataset" || fail=1; \
			elif [ "$(MODE)" = "docker" ]; then \
				$(DOCKER_COMPOSE) --profile processing run --rm processing --model "$$model" --dataset "$$dataset" || fail=1; \
			elif [ "$(MODE)" = "local" ]; then \
				PYTHONPATH=backend-processing/src $(PYTHON) -m processing.main --model "$$model" --dataset "$$dataset" || fail=1; \
			else \
				echo "Invalid MODE: $(MODE)"; exit 1; \
			fi; \
		done; \
	done; \
	exit $$fail

frontend: print-mode
ifeq ($(MODE),release)
	$(DOCKER_COMPOSE_RELEASE) --profile frontend run --rm --service-ports frontend
else ifeq ($(MODE),docker)
	$(DOCKER_COMPOSE) --profile frontend run --rm --service-ports frontend
else ifeq ($(MODE),local)
	cd $(FRONTEND_DIR) && PYTHONPATH=src $(STREAMLIT) run src/webapp/main.py
else
	@echo "Invalid MODE: $(MODE). Use release, docker, or local." && exit 1
endif

# --- Simplified Aliases ---
start: frontend

ingest-all:
	@$(MAKE) ingestion INGEST="all"

process-all:
	@$(MAKE) processing MODELS="lda bertopic top2vec fastopic" DATASETS="readmes issues thesis abstracts"

pipeline: ingest-all process-all start

docker-build: docker-build-ingestion docker-build-processing docker-build-frontend

pull:
	@echo "⬇️ Pulling latest release images..."
	$(DOCKER_COMPOSE_RELEASE) --profile ingestion --profile processing --profile frontend pull

docker-build-ingestion:
	$(DOCKER_COMPOSE) --profile ingestion build

docker-build-processing:
	$(DOCKER_COMPOSE) --profile processing build

docker-build-frontend:
	$(DOCKER_COMPOSE) --profile frontend build
