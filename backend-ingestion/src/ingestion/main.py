import argparse
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from ingestion.application.usecase.data_ingestion_usecase import DataIngestionUsecase
from ingestion.application.usecase.ensure_dataset_consistency_usecase import (
    EnsureDatasetConsistencyUseCase,
)
from ingestion.domain.entities.execution_report import ExecutionReport
from ingestion.domain.entities.ingestion_summary import IngestionSummary
from ingestion.infrastructure.adapter.execution_report_parquet_json_adapter import (
    ExecutionReportParquetJsonAdapter,
)
from ingestion.infrastructure.adapter.github_rest_adapter import GithubRestAdapter
from ingestion.infrastructure.adapter.ingestion_parquet_storage import (
    IngestionParquetStorage,
)
from ingestion.infrastructure.adapter.parquet_dataset_state_adapter import (
    ParquetDatasetStateAdapter,
)
from ingestion.infrastructure.adapter.repo_list_csv_reader import RepoListCsvReaderPort

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def _log_ingestion_summary(summary: IngestionSummary) -> None:
    repos_with_data_list = (
        summary.repos_with_data if isinstance(summary.repos_with_data, list) else []
    )
    repos_without_data_list = (
        summary.repos_without_data
        if isinstance(summary.repos_without_data, list)
        else []
    )
    logger.info(
        "Ingestion summary (%s): with_data=%s without_data=%s",
        summary.data_type,
        summary.with_data_count,
        summary.without_data_count,
    )
    repos_with_data = ", ".join(repos_with_data_list)
    repos_without_data = ", ".join(repos_without_data_list)
    logger.info(
        "Repositories with data (%s): %s",
        summary.data_type,
        repos_with_data if repos_with_data else "None",
    )
    logger.info(
        "Repositories without data (%s): %s",
        summary.data_type,
        repos_without_data if repos_without_data else "None",
    )


def main() -> None:
    """
    Main entrypoint for the ingestion pipeline.
    Reads configuration from environment variables and the repository CSV,
    instantiates adapters and the ingestion use case, and runs the
    ingestion steps.
    Side effects:
    - Creates directories (ingestion output dir).
    - Performs network calls to GitHub (may be rate-limited for unauthenticated
      requests).
    - Writes ingestion output (parquet) to the ingestion output directory.
    - Emits informational and error logs.
    Exceptions:
    - FileNotFoundError when the repos CSV is missing.
    - Re-raises RuntimeError after logging any critical error encountered
    during ingestion.
    Returns:
    - None
    """
    parser = argparse.ArgumentParser(
        description="Data ingestion pipeline for GitHub repositories."
    )
    parser.add_argument(
        "--ingest",
        nargs="+",
        choices=["issues", "readmes", "thesis", "abstracts", "all"],
        default=["all"],
        help="Specify which data to ingest. Use 'all' to ingest all data types. "
        "Can be one or more of: issues, readmes, thesis, abstracts.",
    )
    args = parser.parse_args()

    logger.info("Ingestion Started")

    # --- token form environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.warning(
            "GITHUB_TOKEN environment variable not set. Proceeding with "
            "unauthenticated requests."
        )

    # --- file paths
    project_root = Path(__file__).resolve().parents[3]
    default_data_dir = os.path.join(project_root, "data")
    data_dir = os.getenv("DATA_DIR", default_data_dir)
    ingestion_output_dir = os.path.join(data_dir, "ingestion")

    repos_csv_file_name = os.getenv("REPOS_CSV_FILE_NAME", "tfg_list.csv")
    repos_csv_path = os.path.join(data_dir, repos_csv_file_name)

    logger.info("Data dir: %s", os.path.abspath(data_dir))
    logger.info("Repos CSV: %s", os.path.abspath(repos_csv_path))
    logger.info("Ingestion output dir: %s", os.path.abspath(ingestion_output_dir))

    os.makedirs(ingestion_output_dir, exist_ok=True)

    if not os.path.exists(repos_csv_path):
        raise FileNotFoundError(f"repos.csv not found at {repos_csv_path}")

    # --- adapters
    repo_list_csv_reader = RepoListCsvReaderPort(file_path=repos_csv_path)
    github_rest_adapter = GithubRestAdapter(token=github_token)
    data_parquet_storage = IngestionParquetStorage(base_dir=ingestion_output_dir)
    execution_report_storage = ExecutionReportParquetJsonAdapter(
        base_dir=ingestion_output_dir
    )
    ingestor = DataIngestionUsecase(
        github_port=github_rest_adapter,
        repo_info_reader=repo_list_csv_reader,
        storage_port=data_parquet_storage,
    )
    dataset_state_adapter = ParquetDatasetStateAdapter(
        ingestion_dir=ingestion_output_dir
    )
    logger.info("Ensuring dataset consistency")
    EnsureDatasetConsistencyUseCase(dataset_state_port=dataset_state_adapter).execute(
        repos_csv_path
    )

    ingest_targets = args.ingest
    logger.info("Ingestion targets: %s", ingest_targets)

    run_id = (
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-"
        f"{uuid.uuid4().hex[:8]}"
    )
    run_started_at = datetime.now(timezone.utc)
    execution_status = "success"
    execution_error_message = None
    dataset_summaries: list[IngestionSummary] = []

    try:
        if "all" in ingest_targets or "issues" in ingest_targets:
            logger.info("Ingesting issue data")
            issue_summary = ingestor.ingest_issues_data()
            _log_ingestion_summary(issue_summary)
            dataset_summaries.append(issue_summary)
            logger.info("Ingestion issues Completed")

        if "all" in ingest_targets or "readmes" in ingest_targets:
            logger.info("Ingesting Readme data")
            readme_summary = ingestor.ingest_readme_data()
            _log_ingestion_summary(readme_summary)
            dataset_summaries.append(readme_summary)
            logger.info("Ingestion Readme Completed")

        if "all" in ingest_targets or "thesis" in ingest_targets:
            logger.info("Ingesting Thesis data")
            thesis_summary = ingestor.ingest_thesis_data()
            _log_ingestion_summary(thesis_summary)
            dataset_summaries.append(thesis_summary)
            logger.info("Ingestion Thesis Completed")

        if "all" in ingest_targets or "abstracts" in ingest_targets:
            logger.info("Ingesting abstracts data")
            abstracts_summary = ingestor.ingest_abstracts_data()
            _log_ingestion_summary(abstracts_summary)
            dataset_summaries.append(abstracts_summary)
            logger.info("Ingestion abstracts Completed")

        # Persist thesis metadata
        logger.info("Persisting thesis metadata")
        ingestor.ingest_thesis_metadata()
    except Exception as exc:
        execution_status = "failed"
        execution_error_message = str(exc)
        logger.error("A critical error occurred:%s", exc, exc_info=True)
        raise
    finally:
        run_finished_at = datetime.now(timezone.utc)
        report = ExecutionReport(
            run_id=run_id,
            started_at=run_started_at,
            finished_at=run_finished_at,
            status=execution_status,
            selected_targets=ingest_targets,
            dataset_summaries=dataset_summaries,
            error_message=execution_error_message,
        )
        execution_report_storage.save_execution_report(report)
        logger.info("Execution report persisted for run_id=%s", run_id)


if __name__ == "__main__":
    main()
