# Frontend Web Module

## Overview

This module provides the Streamlit web interface for the TFG Topics project.
It reads precomputed results from the ingestion and processing modules and
offers interactive visual analysis.

The module follows a hexagonal (ports and adapters) architecture with a
`src/` layout.

## Features

- **Model Analysis**:
    - Explore results for one model and one dataset.
    - Includes topic wordclouds, topic summaries, document-topic distribution,
      intertopic distance maps, and hyperparameter plots.
- **Model Comparison**:
    - Compare multiple models (`lda`, `bertopic`, `fastopic`, `top2vec`) on
      the same dataset.
    - Displays aggregated metrics and a final ranking score.
- **Academic Document Analysis**:
    - Focused on the `thesis` dataset.
    - Filters by tutor, year, and grade range.
    - Shows topic frequency and topic distribution by grade category.

## Installation

1. Navigate to the `frontend-web` directory.
2. Install dependencies:

```bash
pip install -r requirement.txt
```

## GitHub Codespaces

The repository devcontainer configures Python 3.10, `PYTHONPATH` for all
`src/` modules, and installs frontend dependencies automatically during
Codespaces creation.

## Running the Module

### Local Python execution

From this directory (`/frontend-web`) run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
streamlit run src/webapp/main.py
```

The UI will be available at `http://localhost:8501`.

## Configuration

Environment variables:

| Variable   | Description                                                               | Default value      |
|------------|---------------------------------------------------------------------------|--------------------|
| `DATA_DIR` | Base directory for ingestion and processing datasets used by the frontend | `<repo_root>/data` |

Expected directories under `DATA_DIR`:

- `ingestion/`
- `processing/`

## Input Data

The frontend consumes precomputed Parquet files.

### Ingestion input

- `ingestion/metadata.parquet`

### Processing input

Files are expected in:
`processing/<model_name>/<dataset>_<suffix>.parquet`

Required suffixes used by the UI:

- `model_summary`
- `metrics`
- `document_topics`
- `topics`
- `params`
- `topic_coordinates`
- `best_hyperparameters`
- `hyperparameter_trials`

Supported datasets:

- `issues`
- `readmes`
- `thesis`
- `abstracts`

Supported models:

- `lda`
- `bertopic`
- `fastopic`
- `top2vec`

## Main Dependencies

- `streamlit`: UI and app routing.
- `pandas` and `pyarrow`: Data loading from Parquet files.
- `plotly` and `matplotlib`: Visualizations.
- `wordcloud`: Topic word cloud rendering.

## Docker

You can build and run this module with Docker Compose from the project root
directory (`/`):

```bash
# Build the frontend image
docker compose --profile frontend build

# Run the frontend container
docker compose --profile frontend run --rm frontend
```

The container exposes Streamlit on port `8501`.
