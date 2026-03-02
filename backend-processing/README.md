# Backend Processing Module

## Overview

This module is responsible for the core data processing and topic modeling tasks of the project. It takes the data prepared by the ingestion module, applies various NLP techniques to clean and process it, and then runs topic modeling algorithms to extract insights.

The module is designed to be flexible, supporting different data sources and topic modeling algorithms.

## Features

-   **Topic Modeling**: Implements several topic modeling algorithms:
    - `LDA (Latent Dirichlet Allocation)`
    - `BERTopic`
    - `FASTopic`
    - `Top2Vec`
-   **Hyperparameter Optimization**: Uses `Optuna` to perform hyperparameter search and find the best parameters for the topic models.
-   **Data Handling**:
    -   Reads data from Parquet files provided by the ingestion module.
    -   Supports different data sources (`readmes`, `issues`, `thesis`, `abstracts`).
    -   Saves all modeling results, including topics, metrics, and hyperparameters, to Parquet files.
-   **Text Processing**: Includes specialized text cleaning and normalization utilities, such as the `LatexTextProcessor` for academic documents.

## Installation

1.  Navigate to the `backend-processing` directory.
2.  Install the required dependencies using pip:

    ```bash
    pip install -r requirements.txt -r requirements-dev.txt
    ```

## GitHub Codespaces

The repository devcontainer configures Python 3.10 and `PYTHONPATH` for the
`src/` layout. In Codespaces, install processing dependencies from the repository
root:

```bash
pip install -r backend-processing/requirements.txt -r backend-processing/requirements-dev.txt
```

## Usage

The main entry point for the module is `src/processing/main.py`. It can be executed from the command line with the following arguments:

-   `--model`: The topic modeling algorithm to use. (Required, e.g., `bertopic`, `lda`)
-   `--dataset`: The data source to process. (Required, e.g., `readmes`, `issues`, `thesis`, `abstracts`)

### Examples

**Running BERTopic on README files:**

```bash
python src/processing/main.py --model bertopic --dataset readmes
```

**Running LDA on GitHub issues:**

```bash
python src/processing/main.py --model lda --dataset issues
```

The script will read the corresponding data from the ingestion output directory, run the topic modeling pipeline, and save the results in the processing output directory.

### Run All Models and Datasets in One Shot

From the repository root, run:

```bash
make processing-all
```

This executes all combinations of:

- Models: `lda`, `bertopic`, `top2vec`, `fastopic`
- Datasets: `readmes`, `issues`, `thesis`, `abstracts`

To run inside Docker instead:

```bash
make processing-all-docker
```

You can also limit the execution scope by overriding variables:

```bash
make processing-all MODELS="bertopic lda" DATASETS="readmes thesis"
```

## Configuration

- **Data Directories**: The input (`ingestion`) and output (`processing`) data directories can be configured via the `DATA_DIR` environment variable. If not set, it defaults to the `data/` directory in the project root.

## Output Files and Format

The module generates several Parquet files containing the results of the hyperparameter search and the topic modeling process. The files are saved under `[DATA_DIR]/processing/[model_name]/`.

### Hyperparameter Search Files

- `[dataset]_hyperparameter_trials.parquet`: Records each trial from the Optuna search.

| Column      | Type   | Description                                    |
|-------------|--------|------------------------------------------------|
| `trial_id`  | int    | ID of the trial.                               |
| `model`     | string | Name of the model.                             |
| `score`     | float  | Performance score for the trial.               |
| `state`     | string | State of the trial (`COMPLETE`, `FAIL`, etc.). |
| `...params` | -      | Columns for each hyperparameter tested.        |

- `[dataset]_best_hyperparameters.parquet`: Stores the best parameters found.

| Column       | Type   | Description                                 |
|--------------|--------|---------------------------------------------|
| `dataset`    | string | Name of the dataset.                        |
| `model`      | string | Name of the model.                          |
| `best_score` | float  | The best score achieved.                    |
| `...params`  | -      | Columns for the best hyperparameter values. |

### Topic Model Result Files

These files share a `run_id` to link them to a specific execution.

- `[dataset]_model_summary.parquet`: Metadata about the model run.

| Column       | Type      | Description          |
|--------------|-----------|----------------------|
| `dataset`    | string    | Name of the dataset. |
| `model_name` | string    | Name of the model.   |
| `model_type` | string    | Type of the model.   |
| `run_id`     | string    | Unique run ID.       |
| `created_at` | timestamp | Creation timestamp.  |
| `num_topics` | int       | Number of topics.    |

- `[dataset]_topics.parquet`: The words that constitute each topic.

| Column       | Type   | Description          |
|--------------|--------|----------------------|
| `dataset`    | string | Name of the dataset. |
| `model_name` | string | Name of the model.   |
| `run_id`     | string | Unique run ID.       |
| `topic_id`   | int    | Topic identifier.    |
| `word`       | string | Word in the topic.   |
| `rank`       | int    | Word rank in topic.  |

- `[dataset]_document_topics.parquet`: The mapping of documents to topics.

| Column        | Type   | Description               |
|---------------|--------|---------------------------|
| `document_id` | string | Document identifier.      |
| `topic_id`    | int    | Topic identifier.         |
| `probability` | float  | Probability of the topic. |

- `[dataset]_metrics.parquet`: Evaluation metrics for the model.

| Column       | Type   | Description          |
|--------------|--------|----------------------|
| `dataset`    | string | Name of the dataset. |
| `model_name` | string | Name of the model.   |
| `run_id`     | string | Unique run ID.       |
| `metric`     | string | Name of the metric.  |
| `value`      | float  | Value of the metric. |

- `[dataset]_params.parquet`: The specific parameters used for the final model run.

| Column       | Type   | Description          |
|--------------|--------|----------------------|
| `dataset`    | string | Name of the dataset. |
| `model_name` | string | Name of the model.   |
| `run_id`     | string | Unique run ID.       |
| `param`      | string | Parameter name.      |
| `value`      | string | Parameter value.     |

- `[dataset]_topic_coordinates.parquet`: 2D or 3D coordinates for topic visualization.

## Main Dependencies

- `pandas` & `pyarrow`: For data manipulation and Parquet file handling.
- `bertopic`, `gensim`, `lda`: For topic modeling.
- `optuna`: For hyperparameter optimization.
- `nltk`, `beautifulsoup4`, `lxml`: For text cleaning and processing.
- `python-dotenv`: For managing environment variables.

## Docker

You can also build and run this module as a Docker container from de root directory of the project `/`

```bash
# Build the image
docker compose --profile processing build

# Run the container (example)
docker compose --profile processing run --rm processing --model bertopic --dataset readmes
```
