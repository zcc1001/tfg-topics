import argparse
import logging
import os
from pathlib import Path

import nltk
from dotenv import load_dotenv

from processing.application.ports.topic_model_port import TopicModelPort
from processing.application.services.hyperparam_service import (
    HyperparameterSearchService,
)
from processing.application.usecases.ensure_processing_dataset_consistency import (
    EnsureProcessingDatasetConsistencyUseCase,
)
from processing.application.usecases.topic_modeling_usecase import TopicModelingUseCase
from processing.infrastructure.adapters.data_parquet_storage_writer import (
    DataParquetStorageWriter,
)
from processing.infrastructure.adapters.modeling.bertopic_model_adapter import (
    BerTopicModelAdapter,
)
from processing.infrastructure.adapters.modeling.fastopic_model_adapter import (
    FastTopicModelAdapter,
)
from processing.infrastructure.adapters.modeling.lda_topic_model_adapter import (
    LdaTopicModelAdapter,
)
from processing.infrastructure.adapters.modeling.top2vec_topic_adapter import (
    Top2VecModelAdapter,
)
from processing.infrastructure.adapters.parquet_dataset_state_adapter import (
    ParquetDatasetStateAdapter,
)
from processing.infrastructure.adapters.parquet_document_reader import (
    ParquetDocumentRepository,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for processing the processing - module ."""
    logger.info("Processing-Module Started...")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", required=True, help="Model to be used for topic modeling"
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Data source to be used",
        choices=["readmes", "issues", "thesis"],
    )
    args = parser.parse_args()

    # in/out paths from environment variables
    project_root = Path(__file__).resolve().parents[3]
    default_data_dir = os.path.join(project_root, "data")
    data_dir = os.getenv("DATA_DIR", default_data_dir)
    ingestion_dir = os.path.join(data_dir, "ingestion")
    processing_dir = os.path.join(data_dir, "processing")

    dataset_state_adapter = ParquetDatasetStateAdapter(
        ingestion_dir=ingestion_dir,
        processing_dir=processing_dir,
    )
    document_repo = ParquetDocumentRepository(ingestion_dir)
    hyperparam_service = HyperparameterSearchService(n_trials=5)
    nltk.download("stopwords")

    model_adapter: TopicModelPort
    if args.model.lower() == "lda":
        model_adapter = LdaTopicModelAdapter()
    elif args.model.lower() == "bertopic":
        model_adapter = BerTopicModelAdapter()
    elif args.model.lower() == "top2vec":
        model_adapter = Top2VecModelAdapter()
    elif args.model.lower() == "fastopic":
        model_adapter = FastTopicModelAdapter()
    else:
        logger.error("Model '%s' is not supported.", args.model)
        return

    writer = DataParquetStorageWriter(
        processing_data_dir=processing_dir, results_filename="results.parquet"
    )
    dataset_hash = EnsureProcessingDatasetConsistencyUseCase(
        dataset_state_port=dataset_state_adapter
    ).execute(
        dataset=args.dataset,
        model_name=args.model.lower(),
    )
    topic_modeling_use_case = TopicModelingUseCase(
        document_repository=document_repo,
        hyperparam_service=hyperparam_service,
        model_adapter=model_adapter,
        writer=writer,
        dataset_hash=dataset_hash,
    )

    topic_modeling_use_case.execute(dataset=args.dataset)
    logger.info("Processing-Module Completed...")


if __name__ == "__main__":
    main()
