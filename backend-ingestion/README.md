# Ingestion Module

This module is responsible for extracting textual data and academic metadata from GitHub repositories that are part of the Final Degree Project (TFG) dataset. 

Its main purpose is to collect, normalize, and persist documents that will be processed later by the `processing` module. This module strictly follows a **Hexagonal (Ports and Adapters) Architecture** in Python 3.10, ensuring a clear separation between core domain logic and external infrastructure concerns.

---

## Architecture Overview

Following the hexagonal design guidelines, the code is structured as follows:

```
src/ingestion/
├── __init__.py
├── logging_config.py      # Logger configuration
├── main.py                # Pipeline entrypoint
├── domain/                # Core business logic and structures
│   ├── __init__.py
│   └── entities/
│       ├── __init__.py
│       ├── entities.py           # Dataclasses (IssueData, ReadmeData, ThesisInfo, etc.)
│       └── ingestion_summary.py  # Ingestion summary data structure
├── application/           # Ports & Use Cases
│   ├── __init__.py
│   ├── ports/             # Abstract Base Classes (interfaces)
│   │   ├── __init__.py
│   │   ├── github_port.py        # Interface for fetching GitHub data
│   │   ├── repo_list_reader.py   # Interface for reading repo list
│   │   └── storage_port.py       # Interface for persisting extracted datasets
│   └── usecase/           # Workflow orchestration
│       ├── __init__.py
│       └── data_ingestion_usecase.py # Data ingestion application workflow
└── infrastructure/        # Adapters (Implementation of ports)
    ├── __init__.py
    └── adapter/
        ├── __init__.py
        ├── data_parquet_storage.py      # (Legacy) Storage implementation
        ├── github_rest_adapter.py       # GitHub REST API & LaTeX parser adapter
        ├── ingestion_parquet_storage.py # Storage implementation using pyarrow
        └── repo_list_csv_reader.py      # CSV loader & URL parser adapter
```

> [!NOTE]
> All core business workflows depend exclusively on **Ports** (interfaces). Concrete **Adapters** are injected at the application boundary in `main.py`, making the domain fully independent of third-party REST APIs or storage libraries.

---

## Data Pipeline Input & Output

### 1. Input: Repository List (`tfg_list.csv`)

The pipeline requires a repository list in CSV format (by default `tfg_list.csv` in the data directory). 

> [!IMPORTANT]
> **Header Requirement**: The CSV file **must contain all 7 headers** in its first line (in any order, though the default order is shown below). If any header is missing, the Pandas parser will raise an `AttributeError` and fail.
>
> **Row-level Requirement**: For individual rows, only `repository_url` is strictly required to have a value. The other metadata values can be left blank (empty cells), and the parser will automatically normalize them to empty strings.

The 7 columns in the exact order of the default `tfg_list.csv` file:

| Column | Type | Value Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | String | No | Academic title of the final degree project. |
| `tutors` | String | No | Supervisor or tutors of the project (can contain multiple names). |
| `students` | String | No | Student(s) who authored the project. |
| `assignment_date` | String | No | Date when the project was officially assigned (format: `DD/MM/YYYY`). |
| `presentation_date` | String | No | Date when the project was defended (format: `DD/MM/YYYY`). |
| `grade` | String | No | Numeric grade obtained (supports comma/dot decimal separators). |
| `repository_url` | String | **Yes** | GitHub URL used to infer `repo_owner/repo_name` (supports HTTPS and SSH formats). |

#### Minimal Input Example (With All Required Headers)
```csv
title,tutors,students,assignment_date,presentation_date,grade,repository_url
,,,01/01/2025,15/07/2025,9.5,https://github.com/owner-one/tfg-project-a
,,,10/11/2024,20/09/2025,8.7,https://github.com/owner-two/tfg-project-b
```

---

### 2. Output Format

All extracted data is stored in **Apache Parquet format** in the `/data/ingestion` directory. The pipeline produces up to five independent datasets:

```
data/ingestion/
├── abstracts.parquet
├── issues.parquet
├── metadata.parquet
├── readmes.parquet
└── thesis.parquet
```

---

### 3. Parquet Schemas

The following sections define the exact schemas of the generated Parquet files (serialized directly from core domain entities):

#### A. Issues Dataset (`issues.parquet`)
Each row corresponds to a single GitHub issue. Pull requests are automatically filtered out.

| Column | Type | Description |
| :--- | :--- | :--- |
| `thesis_id` | Int64 | Unique project identifier derived from the CSV row index |
| `repo_owner` | String | GitHub repository owner/organization |
| `repo_name` | String | GitHub repository name |
| `issue_id` | Int64 | GitHub issue number |
| `title` | String | Issue title |
| `description` | String | Raw text content of the issue body |
| `retrieved_at` | Timestamp | Timestamp when the data was extracted (UTC) |

#### B. README Dataset (`readmes.parquet`)
Each row corresponds to a repository's default branch README file. Preserves markdown syntax.

| Column | Type | Description |
| :--- | :--- | :--- |
| `thesis_id` | Int64 | Unique project identifier |
| `download_url` | String | Raw download URL of the README file |
| `content` | String | Raw textual content of the README (including markdown styling) |
| `retrieved_at` | Timestamp | Timestamp when the README was extracted (UTC) |

#### C. Thesis Dataset (`thesis.parquet`)
Each row corresponds to a project's technical report sections. The module downloads and extracts specific LaTeX files in the repository (e.g., `tex/1_Introduccion.tex` to `tex/7_Conclusiones_Lineas_de_trabajo_futuras.tex`).

| Column | Type | Description |
| :--- | :--- | :--- |
| `thesis_id` | Int64 | Unique project identifier |
| `texts` | List of Structs | Array of documents extracted. Each struct contains:<br>- `contents` (String): Raw text from the LaTeX section file<br>- `section` (String): The base name of the LaTeX file (e.g., `1_Introduccion`) |
| `retrieved_at` | Timestamp | Timestamp when the LaTeX files were extracted (UTC) |

#### D. Abstracts Dataset (`abstracts.parquet`)
Each row corresponds to the extracted academic abstract from `memoria.tex`. The parser automatically identifies LaTeX abstract blocks and filters out keyword lists.

| Column | Type | Description |
| :--- | :--- | :--- |
| `thesis_id` | Int64 | Unique project identifier |
| `repo_owner` | String | GitHub repository owner/organization |
| `repo_name` | String | GitHub repository name |
| `source_path` | String | Path where `memoria.tex` was found in the repository |
| `content` | String | Extracted abstract text |
| `retrieved_at` | Timestamp | Timestamp when the abstract was extracted (UTC) |

#### E. Thesis Metadata Dataset (`metadata.parquet`)
This dataset maps and persists academic metadata for downstream processing, automatically converting grades to floats and dates to defense years.

| Column | Type | Description |
| :--- | :--- | :--- |
| `thesis_id` | Int64 | Unique project identifier |
| `title` | String | TFG title |
| `tutor` | String | Supervisor or tutors of the project |
| `student` | String | Student author |
| `year` | Int64 (Nullable) | Defense year extracted from `presentation_date` |
| `grade` | Float64 (Nullable) | Numeric grade (normalized to use decimal dot) |
| `repository_url` | String | Full GitHub repository URL |
| `repo_owner` | String | Extracted GitHub owner name |
| `repo_name` | String | Extracted GitHub repository name |

---

## Configuration & Environment

You can configure the pipeline's behavior using the following environment variables:

| Variable | Description | Default Value |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | GitHub Personal Access Token (PAT) for authenticated requests. | `None` (Unauthenticated, strictly rate-limited) |
| `DATA_DIR` | Base directory for input CSV and output Parquet directories. | `/data` (within Docker) or project-root `/data` (locally) |
| `REPOS_CSV_FILE_NAME` | Name of the CSV file containing the target repository list. | `tfg_list.csv` |

### Setting Up Configuration

1. **Option A: `.env` file**  
   Create a `.env` file directly under the `/backend-ingestion` directory:
   ```env
   GITHUB_TOKEN="ghp_yourPersonalAccessTokenHere"
   DATA_DIR="./data"
   REPOS_CSV_FILE_NAME="tfg_list.csv"
   ```

2. **Option B: Shell Export**  
   Export the variables in your terminal before launching the pipeline:
   ```bash
   export GITHUB_TOKEN=ghp_yourPersonalAccessTokenHere
   export DATA_DIR=/path/to/my/data
   ```

> [!WARNING]
> Unauthenticated requests to the GitHub API are capped at 60 requests per hour. It is highly recommended to supply a valid `GITHUB_TOKEN` (which boosts the rate limit to 5000 requests per hour).

---

## Running the Ingestion Module

### Approach 1: Using the Root `Makefile` (Recommended)

From the project **root** directory (`/`), you can seamlessly orchestrate local or containerized execution:

* **Local Python execution (all targets)**:
  ```bash
  make ingestion MODE=local
  ```
* **Local Python execution (specific targets)**:
  ```bash
  make ingestion MODE=local INGEST="issues readmes"
  ```
* **Production/Pre-built Docker execution (recommended)**:
  ```bash
  make ingestion MODE=release INGEST="all"
  ```
* **Local Docker Build & execution**:
  ```bash
  make ingestion MODE=docker INGEST="all"
  ```

---

### Approach 2: Running Directly with Local Python

If you prefer to run it manually from this directory (`/backend-ingestion`):

1. **Set up the virtual environment and activate it**:
   ```bash
   python -m venv .venv
   
   # Windows (PowerShell/CMD)
   .venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```

3. **Run the entrypoint script**:
   ```bash
   # Run all ingestion pipelines
   python src/ingestion/main.py
   
   # Run specific target ingestion pipelines
   python src/ingestion/main.py --ingest issues readmes
   ```

---

### Approach 3: Containerized via Docker Compose

From the project root directory (`/`), run:

```bash
# Build the Docker image
docker compose --profile ingestion build

# Execute the ingestion pipeline containerized
docker compose --profile ingestion run --rm ingestion --ingest all
```

---

## Quality Assurance & Testing

The ingestion module includes a comprehensive suite of unit and integration tests.

To run tests and check code quality from this directory (`/backend-ingestion`):

```bash
# Execute pytest suite
pytest

# Execute pytest with code coverage (requires pytest-cov)
pytest --cov=src
```
