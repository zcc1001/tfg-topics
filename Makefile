.PHONY: \
	help \
	ingestion \
	processing \
	processing-single \
	frontend \
	print-mode \
	start \
	ingest-all \
	process-all \
	pipeline \
	pull \
	docker-build docker-build-ingestion docker-build-processing docker-build-frontend

ifeq ($(OS),Windows_NT)
SHELL := cmd
.SHELLFLAGS := /C
RUN_INGEST_LOCAL = set PYTHONPATH=backend-ingestion/src&& $(PYTHON) -m ingestion.main --ingest $(INGEST)
RUN_PROCESSING_LOCAL = set PYTHONPATH=backend-processing/src&& $(PYTHON) -m processing.main --model "$(MODEL)" --dataset "$(DATASET)"
RUN_FRONTEND_LOCAL = cd $(FRONTEND_DIR) && set PYTHONPATH=src&& $(STREAMLIT) run src/webapp/main.py
else
SHELL := /bin/sh
.SHELLFLAGS := -ec
RUN_INGEST_LOCAL = PYTHONPATH=backend-ingestion/src $(PYTHON) -m ingestion.main --ingest $(INGEST)
RUN_PROCESSING_LOCAL = PYTHONPATH=backend-processing/src $(PYTHON) -m processing.main --model "$(MODEL)" --dataset "$(DATASET)"
RUN_FRONTEND_LOCAL = cd $(FRONTEND_DIR) && PYTHONPATH=src $(STREAMLIT) run src/webapp/main.py
endif

PYTHON ?= python
STREAMLIT ?= streamlit
DOCKER_COMPOSE ?= docker compose
DOCKER_COMPOSE_RELEASE ?= $(DOCKER_COMPOSE) -f docker-compose.release.yml
FRONTEND_DIR ?= frontend-web

INGEST ?= all
MODELS ?= bertopic
DATASETS ?= abstracts

MODE ?= release

PROCESSING_TARGETS := $(foreach model,$(MODELS),$(foreach dataset,$(DATASETS),processing-$(model)-$(dataset)))

define REGISTER_PROCESSING_TARGET
processing-$(1)-$(2):
	@"$(MAKE)" --no-print-directory processing-single MODE=$(MODE) MODEL="$(1)" DATASET="$(2)"
endef

$(foreach model,$(MODELS),$(foreach dataset,$(DATASETS),$(eval $(call REGISTER_PROCESSING_TARGET,$(model),$(dataset)))))

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
	$(RUN_INGEST_LOCAL)
else
	@echo "Invalid MODE: $(MODE). Use release, docker, or local." && exit 1
endif

processing: print-mode $(PROCESSING_TARGETS)

processing-single:
	@echo ">>> processing model=$(MODEL) dataset=$(DATASET) (mode: $(MODE))"
ifeq ($(MODE),release)
	$(DOCKER_COMPOSE_RELEASE) --profile processing run --rm processing --model "$(MODEL)" --dataset "$(DATASET)"
else ifeq ($(MODE),docker)
	$(DOCKER_COMPOSE) --profile processing run --rm processing --model "$(MODEL)" --dataset "$(DATASET)"
else ifeq ($(MODE),local)
	$(RUN_PROCESSING_LOCAL)
else
	@echo "Invalid MODE: $(MODE). Use release, docker, or local." && exit 1
endif

frontend: print-mode
ifeq ($(MODE),release)
	$(DOCKER_COMPOSE_RELEASE) --profile frontend run --rm --service-ports frontend
else ifeq ($(MODE),docker)
	$(DOCKER_COMPOSE) --profile frontend run --rm --service-ports frontend
else ifeq ($(MODE),local)
	$(RUN_FRONTEND_LOCAL)
else
	@echo "Invalid MODE: $(MODE). Use release, docker, or local." && exit 1
endif

# --- Simplified Aliases ---
start: frontend

ingest-all:
	@"$(MAKE)" ingestion INGEST="all"

process-all:
	@"$(MAKE)" processing MODELS="lda bertopic top2vec fastopic" DATASETS="readmes issues thesis abstracts"

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
