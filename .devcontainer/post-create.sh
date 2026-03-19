#!/usr/bin/env bash

set -euo pipefail

python -m pip install --upgrade pip

pip install \
  black \
  flake8 \
  isort \
  mypy \
  pre-commit \
  pytest \
  pytest-cov \
  pytest-mock

pip install \
  -r backend-ingestion/requirements.txt \
  -r backend-ingestion/requirements-dev.txt \
  -r backend-processing/requirements.txt \
  -r backend-processing/requirements-dev.txt \
  -r frontend-web/requirement.txt

pre-commit install
