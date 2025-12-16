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
└── readmes.parquet
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

The ingestion module produces two independent datasets, one for GitHub issues and one for README documents.
All outputs are stored in Apache Parquet format to ensure efficient downstream processing.

Generate files:

- issues.parquet
- readmes.parquet

### Issues dataset
- Text content is stored without NLP preprocessing
- Each issue is treated as an independent document
- Each row corresponds to a single GitHub issue.

| columm      | type   | description             |
|-------------|--------|-------------------------|
| repo_name   | string | Repository name         |
| repo_owner  | string | Repository owner        |
| issue_id    | int    | GitHub issue identifier |
| title       | string | Issue title             |
| description | string | Issue body (raw text)   |

### README dataset
- Each row corresponds to a repository README file.
- README files are stored in raw textual form
- Markdown syntax is preserved

| columm           | type       | description            |
|------------------|------------|------------------------|
| repo_name        | string     | Repository name        |
| repo_owner       | string     | Repository owner       |
| content          | string     | Raw README text        |
| retrieved_at     | timestamp  | Extraction timestamp   |

## Configuration

Environment variables:

| Varibale            | Description                                                     |
|---------------------|-----------------------------------------------------------------|
| GITHUB_TOKEN        | GitHub personal access token (must be obtain in github websiet) |
| DATA_DIR            | Base directory for input/output data                            |  
| REPOS_CSV_FILE_NAME | repository list file name                                       |

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

from actual directory `/ingestion` execute:

```shell
# create virtual env
python -m venv .venv

# activar entorno virtual linux:
source .venv\Scripts\activate

# install python packages
pip install requirements.txt

# run app
python src/main.py
```

### Docker compose (recommended)

From root directory `/` execute:

```shell
docker compose build ingestion 
docker compose --profile ingestion run --rm ingestion
```


