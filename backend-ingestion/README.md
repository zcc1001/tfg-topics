# Ingestion Module

This module is responsible for extracting textual data from GitHub repositories that are part of TFG dataset.
Its main porpose is to collect normalize, and persist documents that will be later processed by the `processing module`.
This module follows a hexagonal (ports and adapters) architecture, ensuring a clear separation between domain logic and
infrastructure concerns.

## Output format

All extracted data is stored in `Apache Parquet format` in following path:

```
/data/ingestion
├── issues.parquet
├── readmes.parquet
└── thesis.parquet
```

## Input and Output

### Input

This module requires a repository list file defined in `repos.csv`

| columm | Type   | Description     |
|--------|--------|-----------------|
| owner  | string | github username |
| name   | string | repository name |

Example:

```csv
owner,name
apache,spark
pallets,flask
scikit-learn,scikit-learn
```

### Output

The ingestion module produces three independent datasets, one for GitHub issues, one for README documents, and one for thesis documents.
All outputs are stored in Apache Parquet format to ensure efficient downstream processing.

Generate files:

- issues.parquet
- readmes.parquet
- thesis.parquet

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
pip install -r requirements.txt

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
docker compose build ingestion

# Run the ingestion container
docker compose --profile ingestion run --rm ingestion
```

By default, this will ingest all data types (`issues`, `readmes`, and `thesis`). You can specify which data to ingest by overriding the entrypoint:

```shell
docker compose --profile ingestion run --rm ingestion --ingest issues 
```
