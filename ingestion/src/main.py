import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from application.usecase.data_ingestion_usecase import DataIngestionUsecase
from infrastructure.adapter.data_parquet_storage import ParquetStorage
from infrastructure.adapter.github_rest_adapter import GithubRestAdapter
from infrastructure.adapter.repo_list_csv_reader import RepoListCsvReaderPort

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Ingestion Started")

    # Lee el token de GitHub de una variable de entorno
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.warning("GITHUB_TOKEN environment variable not set. Proceeding with unauthenticated requests.")

    # Calculo de rutas de salida/entrada ficheros
    project_root = Path(__file__).resolve().parents[2]
    default_data_dir = os.path.join(project_root, "data")
    data_dir = os.getenv("DATA_DIR", default_data_dir)
    ingestion_output_dir = os.path.join(data_dir, "ingestion")

    repos_csv_file_name = os.getenv("REPOS_CSV_FILE_NAME", "repos.csv")
    repos_csv_path = os.path.join(data_dir, repos_csv_file_name)

    logger.info("Data dir: %s", os.path.abspath(data_dir))
    logger.info("Repos CSV: %s", os.path.abspath(repos_csv_path))
    logger.info("Ingestion output dir: %s", os.path.abspath(ingestion_output_dir))

    os.makedirs(ingestion_output_dir, exist_ok=True)

    if not os.path.exists(repos_csv_path):
        raise FileNotFoundError(f"repos.csv not found at {repos_csv_path}")

    # adapters
    repo_list_csv_reader = RepoListCsvReaderPort(file_path=repos_csv_path)
    github_rest_adapter = GithubRestAdapter(token=github_token)
    data_parquet_storage = ParquetStorage(base_dir=ingestion_output_dir)
    ingestor = DataIngestionUsecase(github_port=github_rest_adapter, repo_info_reader=repo_list_csv_reader,
                                    storage_port=data_parquet_storage)

    try:
        logger.info("Ingesting issue date")
        ingestor.ingest_issues_data()
        logger.info("Ingestion issues Completed")

        logger.info("Ingesting Readme data")
        ingestor.ingest_readme_data()
        logger.info("Ingestion Readme Completed")
    except RuntimeError as e:
        logger.error(f"A critical error occurred: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
