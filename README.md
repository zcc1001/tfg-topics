# TFG: Qualitative Thematic Analysis of Final Degree Projects

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub issues](https://img.shields.io/github/issues-closed/zcc1001/tfg-topics)](https://github.com/zcc1001/tfg-topics/issues)
[![Wiki](https://img.shields.io/badge/wiki-available-brightgreen)](https://github.com/zcc1001/tfg-topics/wiki)
[![GitHub Release](https://img.shields.io/github/v/release/zcc1001/tfg-topics?label=Release)](https://github.com/zcc1001/tfg-topics/releases)
[![Zube](https://img.shields.io/badge/zube-managed-blue?logo=zube)](https://zube.io/)
[![CI](https://github.com/zcc1001/tfg-topics/actions/workflows/ci.yml/badge.svg)](https://github.com/zcc1001/tfg-topics/actions/workflows/ci.yml)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=zcc1001_tfg-topics&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=zcc1001_tfg-topics)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=zcc1001_tfg-topics&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=zcc1001_tfg-topics)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=zcc1001_tfg-topics&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=zcc1001_tfg-topics)

## 📜 Description

This project focuses on developing an application for qualitative thematic analysis of the text contained in Final Degree Project (TFG) reports. The goal is to assist both faculty and students in interpreting and searching for information within reports from previous academic years.

The datasets are generated from the textual information of TFG reports available in LaTeX format on GitHub. The project implements and evaluates the performance of multiple topic modeling algorithms.

## ✨ Features

- **Data Ingestion**: Automatically fetches TFG report data from GitHub repositories.
- **Text Preprocessing**: Cleans and prepares the text for analysis.
- **Topic Modeling**: Implements multiple algorithms to identify underlying themes.
- **Hyperparameter Optimization**: Automatically finds the best parameters for each model.
- **API & Web Interface**: Exposes the results through a simple web interface.

## 🤖 Algorithms

The project explores and compares several state-of-the-art topic modeling techniques:

- [**LDA (Latent Dirichlet Allocation)**](https://github.com/lda-project/lda): A classic probabilistic approach for topic modeling.
- [**Top2Vec**](https://github.com/ddangelov/Top2Vec): Leverages joint word and document embeddings to find topics.
- [**BERTopic**](https://github.com/MaartenGr/BERTopic): Uses BERT embeddings and a class-based TF-IDF to create dense clusters.
- [**FASTopic**](https://github.com/bobxwu/FASTopic): A modern and efficient topic modeling approach.

## 📂 Project Structure

The project is organized into several key directories:

- **`/backend-ingestion`**: Contains the logic for data collection from GitHub.
- **`/backend-processing`**: Includes scripts for text preprocessing, topic modeling, and hyperparameter tuning.
- **`/frontend-web`**: A simple web interface to display the results.
- **`/data`**: Stores the raw and processed data.
- **`/prototypes`**: Jupyter notebooks for experimentation and prototyping.
- **`/docs`**: Project documentation.

## ⚙️ Installation

### Prerequisites

For standard usage:
- **Git**
- **Docker** (Docker Desktop on Windows/Mac, or Docker Engine on Linux)

For local development (optional):
- Conda
- Python 3.10

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/zcc1001/tfg-topics
   cd tfg-topics
   ```

2. **You are ready!** Proceed to the Makefile Usage section below. You do not need to install Python dependencies if you use the default Docker execution mode.

### 🚀 Try it without code (Frontend Only)

If you only want to visualize results and don't want to clone the repository, you can use the sample data from the latest release:

1. Create an empty folder anywhere on your computer.
2. Download `example-data.zip` and `docker-compose.release.yml` from the [Releases page](https://github.com/zcc1001/tfg-topics/releases).
3. Extract `example-data.zip` into your folder (this should create a `data/` folder next to the `docker-compose.release.yml` file).
4. Open your terminal in that folder and run:

   ```bash
   docker compose -f docker-compose.release.yml --profile frontend run --rm frontend
   ```

5. Open `http://localhost:8501` in your browser.

## 🛠️ Makefile Usage

The repository includes a `Makefile` to run ingestion, processing, the frontend, and
the Docker workflow with consistent commands.

To list the available targets and examples:

```bash
make help
```

### Execution Options (The Simple Way)

The default execution `MODE` is `release`, which means **Docker will automatically download pre-built images from GitHub Container Registry**. You do not need to install Python or any dependencies locally to use these commands—just Docker!

- **Start the web application**:
  ```bash
  make start
  ```

- **Run full data ingestion**:
  ```bash
  make ingest-all
  ```

- **Run full processing** (all models and datasets):
  ```bash
  make process-all
  ```

- **Run the entire pipeline sequentially** (ingestion, processing, and frontend):
  ```bash
  make pipeline
  ```

### Advanced Usage & Variables

If you need fine-grained control over which models or datasets to run, or if you want to run the code locally without Docker, the `Makefile` exposes several variables:

- `MODE`: `release` (default, pre-built Docker), `docker` (local Docker build), `local` (pure Python environment).
- `INGEST`: Which data to ingest (`all`, `issues`, `readmes`, `thesis`, `abstracts`).
- `MODELS`: Space-separated list of models (e.g., `"lda bertopic top2vec fastopic"`).
- `DATASETS`: Space-separated list of datasets (e.g., `"readmes issues thesis abstracts"`).

**Example of advanced processing** (running only LDA and BERTopic on thesis data using a local Python environment):

```bash
make processing MODELS="lda bertopic" DATASETS="thesis" MODE=local
```

Alternatively, you can just download the `docker-compose.release.yml` file, place it in an empty directory, create a `data/` folder, and run:
```bash
docker compose -f docker-compose.release.yml --profile frontend run --rm frontend
```

### Docker Lifecycle

Use these targets to build and manage the full containerized environment when using `MODE=docker`:

```bash
make docker-build
make docker-build-ingestion
make docker-build-processing
make docker-build-frontend
```

## 👨‍💻 Contributing & Local Development

If you intend to modify the source code, you may want to set up a pure Python local environment instead of relying solely on Docker.

### Local Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/zcc1001/tfg-topics
   cd tfg-topics
   ```

2. **Create and activate the Conda environment:**

   ```shell
   conda env create -f environment.yml
   conda activate tfg-topics
   ```

3. **Install development tools:**

   ```shell
   pip install black isort flake8 mypy pre-commit
   pre-commit install
   ```

4. **Install project dependencies (per module):**

   ```shell
   pip install -r backend-ingestion/requirements.txt -r backend-ingestion/requirements-dev.txt
   pip install -r backend-processing/requirements.txt -r backend-processing/requirements-dev.txt
   pip install -r frontend-web/requirement.txt
   ```

### GitHub Codespaces Setup

This repository includes a devcontainer config at `.devcontainer/devcontainer.json`.
When opened in Codespaces it provisions Python 3.10, development tools, configures
`PYTHONPATH` for the `src/` modules, and installs the dependencies for ingestion,
processing, and frontend automatically during `postCreateCommand`.
