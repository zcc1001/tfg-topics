# TFG: Qualitative Thematic Analysis of Final Degree Projects
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub issues](https://img.shields.io/github/issues-closed/zcc1001/tfg-topics)](https://github.com/zcc1001/tfg-topics/issues)
[![Wiki](https://img.shields.io/badge/wiki-available-brightgreen)](https://github.com/zcc1001/tfg-topics/wiki)
![GitHub Release](https://img.shields.io/github/v/release/zcc1001/tfg-topics?label=Release)
[![Zube](https://img.shields.io/badge/zube-managed-blue?logo=zube)](https://zube.io/)
[![CI](https://github.com/zcc1001/tfg-topics/actions/workflows/ci.yml/badge.svg)](https://github.com/zcc1001/tfg-topics/actions/workflows/ci.yml)

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
- **`/frontent-web`**: A simple web interface to display the results.
- **`/data`**: Stores the raw and processed data.
- **`/prototypes`**: Jupyter notebooks for experimentation and prototyping.
- **`/docs`**: Project documentation.

## ⚙️ Installation

### Prerequisites

- Conda
- Git
- Python: 3.10

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
When opened in Codespaces it provisions Python 3.10, development tools, and configures
`PYTHONPATH` for the `src/` modules.

After the container is created, install dependencies only for the module(s) you are
working on:

```bash
pip install -r backend-ingestion/requirements.txt -r backend-ingestion/requirements-dev.txt
pip install -r backend-processing/requirements.txt -r backend-processing/requirements-dev.txt
pip install -r frontend-web/requirement.txt
```



