import logging
import os
from dotenv import load_dotenv

from ingestion.src.application.usecase.data_ingestion_usecase import DataIngestionUsecase
from ingestion.src.infrastructure.adapter.data_parquet_storage import ParquetStorage
from ingestion.src.infrastructure.adapter.github_rest_adapter import GithubRestAdapter
from ingestion.src.infrastructure.adapter.repo_list_csv_reader import RepoListCsvReaderPort

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

    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Directorio actual: {current_dir}")

    data_dir = os.path.join(current_dir, "data")
    logger.info(f"Directorio de datos: {data_dir}")
    
    # ruta al fichero CSV
    csv_file_path = os.path.join(data_dir, "repos.csv")
    
    logger.info(f"Buscando repos.csv en: {csv_file_path}")
    logger.info(f"Guardando datos en: {data_dir}")
    # --------------------------------

    repo_list_csv_reader = RepoListCsvReaderPort(file_path=csv_file_path)

    github_rest_adapter = GithubRestAdapter(token=github_token)
    
    data_parquet_storage = ParquetStorage(base_dir=data_dir)

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


if __name__ == "__main__":
    main()
