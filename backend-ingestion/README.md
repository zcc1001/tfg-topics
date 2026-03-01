# Ingestion Module

This module is responsible for extracting textual data from GitHub repositories that are part of TFG dataset.
Its main porpose is to collect normalize, and persist documents that will be later processed by the `processing module`.
This module follows a hexagonal (ports and adapters) architecture, ensuring a clear separation between domain logic and
infrastructure concerns.

## Output format

All extracted data is stored in `Apache Parquet format` in following path:

```
/data/ingestion
├── abstracts.parquet
├── execution_history.parquet
├── issues.parquet
├── metadata.parquet
├── readmes.parquet
├── thesis.parquet
└── executions/
    └── <run_id>/
        └── manifest.json
```

## Input and Output

### Input

This module requires a repository list file (default: `tfg_list.csv`) with at least:

| column          | Type   | Description                                     |
|-----------------|--------|-------------------------------------------------|
| repository_url  | string | GitHub URL used to infer `repo_owner/repo_name` |

Optional metadata columns (used for `metadata.parquet`):
- `title`, `tutors`, `students`, `presentation_date`, `assignment_date`, `grade`

Minimal example:

```csv
repository_url
https://github.com/apache/spark
https://github.com/pallets/flask
https://github.com/scikit-learn/scikit-learn
```

### Output

The ingestion module produces four independent datasets: GitHub issues, README documents, thesis sections, and thesis abstracts.
All outputs are stored in Apache Parquet format to ensure efficient downstream processing.

Generate files:

- issues.parquet
- readmes.parquet
- thesis.parquet
- abstracts.parquet
- metadata.parquet

### Issues dataset

- Text content is stored without NLP preprocessing
- Each issue is treated as an independent document
- Each row corresponds to a single GitHub issue.

| columm       | type      | description             |
|--------------|-----------|-------------------------|
| repo_name    | string    | Repository name         |
| repo_owner   | string    | Repository owner        |
| issue_id     | int       | GitHub issue identifier |
| title        | string    | Issue title             |
| body         | string    | Issue body              |
| description  | string    | Issue body (raw text)   |
| retrieved_at | timestamp | Extraction timestamp    |

### README dataset

- Each row corresponds to a repository README file.
- README files are stored in raw textual form
- Markdown syntax is preserved

| columm       | type      | description          |
|--------------|-----------|----------------------|
| repo_name    | string    | Repository name      |
| repo_owner   | string    | Repository owner     |
| content      | string    | Raw README text      |
| retrieved_at | timestamp | Extraction timestamp |

### Thesis dataset

- Each row corresponds to a section of a thesis document.
- The module searches for specific LaTeX files in the repository.

| columm          | type      | description                                      |
|-----------------|-----------|--------------------------------------------------|
| repo_name       | string    | Repository name                                  |
| repo_owner      | string    | Repository owner                                 |
| text[].contents | string    | Raw text from the LaTeX file                     |
| text[].section  | string    | The name of the section (e.g., `1_Introduccion`) |
| retrieved_at    | timestamp | Extraction timestamp                             |

### Abstracts dataset

- Each row corresponds to one extracted abstract from `memoria.tex`.
- The parser ignores abstract blocks labeled as keywords.

| columm       | type      | description                           |
|--------------|-----------|---------------------------------------|
| thesis_id    | int       | Internal thesis identifier            |
| repo_owner   | string    | Repository owner                      |
| repo_name    | string    | Repository name                       |
| source_path  | string    | Path of the `memoria.tex` file        |
| content      | string    | Extracted abstract text               |
| retrieved_at | timestamp | Extraction timestamp                  |

### Execution reporting output

Each ingestion run persists execution metadata:

- `executions/<run_id>/manifest.json`: run status, selected datasets, counts, and repo lists with and without data.
- `execution_history.parquet`: append-only history with one row per `run_id + dataset + repo`.

`execution_history.parquet` columns:
- `run_id`
- `dataset`
- `repo_owner`
- `repo_name`
- `has_data`
- `records_count`
- `executed_at`
- `status`
- `error_message`

## Configuration

Environment variables:

| Varibale            | Description                                                     | Default value |
|---------------------|-----------------------------------------------------------------|---------------|
| GITHUB_TOKEN        | GitHub personal access token (must be obtain in github websiet) | `null`        |
| DATA_DIR            | Base directory for input/output data                            | `./data`      |
| REPOS_CSV_FILE_NAME | repository list file name                                       | `repos.csv`   |

you can set this vatiables via `.env` file set in this directory with the following format:

```
GITHUB_TOKEN="token"
```

or you can export variables before execution:

```shell
export GITHUB_TOKEN=ghp_xxx
export DATA_DIR=/data
```

## Installation

From this directory (`/backend-ingestion`) install dependencies with:

```shell
pip install -r requirements.txt -r requirements-dev.txt
```

## GitHub Codespaces

The repository devcontainer already configures Python 3.10 and `PYTHONPATH` for the
`src/` layout. In Codespaces, install ingestion dependencies from the repository root:

```bash
pip install -r backend-ingestion/requirements.txt -r backend-ingestion/requirements-dev.txt
```

## Running module

### Local python execution (optional)

From this directory (`/backend-ingestion`) execute:

```shell
# create virtual env
python -m venv .venv

# activate virtual environment (Windows)
.venv\Scripts\activate

# activate virtual environment (Linux/macOS)
# source .venv/bin/activate

# install python packages
pip install -r requirements.txt -r requirements-dev.txt

# run app
python src/ingestion/main.py
```

You can also specify which data to ingest using the `--ingest` flag:

```shell
python src/ingestion/main.py --ingest issues readmes
```

### Docker compose (recommended)

From the root directory of the project (`/`) execute:

```shell
# Build the ingestion image
docker compose --profile ingestion build

# Run the ingestion container
docker compose --profile ingestion run --rm ingestion
```

By default, this will ingest all data types (`issues`, `readmes`, `thesis`, and `abstracts`). You can specify which data to ingest by overriding the entrypoint:

```shell
docker compose --profile ingestion run --rm ingestion --ingest issues 
```
