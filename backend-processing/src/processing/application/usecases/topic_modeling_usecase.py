import logging
import time
from datetime import datetime, timezone

from processing.application.ports.document_repository import DocumentRepository
from processing.application.ports.storage_port import StoragePort
from processing.application.ports.topic_model_port import TopicModelPort
from processing.application.services.hyperparam_service import (
    HyperparameterSearchService,
)

logger = logging.getLogger(__name__)


class TopicModelingUseCase:
    """Topic modeling use case."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        hyperparam_service: HyperparameterSearchService,
        model_adapter: TopicModelPort,
        writer: StoragePort,
    ):
        self.document_repository = document_repository
        self.hyperparam_service = hyperparam_service
        self.model_adapter = model_adapter
        self.writer = writer

    def execute(self, dataset: str) -> None:
        """Execute the search and return the result .

        Args:
            dataset (str): dataset file name without extension.
        """
        logger.info("Starting topic modeling use case.")
        documents = self.document_repository.load_documents(
            doc_name=f"{dataset}.parquet"
        )
        texts = [d.text for d in documents]
        logger.info("Loaded %d documents.", len(texts))

        logger.info("Starting hyperparameter search.")
        start_time = time.time()
        search_result = self.hyperparam_service.search(
            dataset=dataset, model_wrapper=self.model_adapter, texts=texts
        )
        end_time = time.time()
        hyperparam_duration = end_time - start_time

        logger.info("Starting final training.")
        start_time = time.time()
        topic_result = self.model_adapter.fit(
            dataset=dataset, texts=texts, params=search_result.best_params
        )
        end_time = time.time()
        training_duration = end_time - start_time

        self.writer.write_hyperparameter_search(
            result=search_result,
        )
        self.writer.write_topic_model_result(
            result=topic_result,
            run_id=self._generate_run_id(
                model_name=self.model_adapter.model_name(),
                strategy="hyperparameter_search",
            ),
        )

        logger.info(
            "Hyperparameter search finished in %.2f seconds.", hyperparam_duration
        )
        logger.info("Final training finished in %.2f seconds.", training_duration)
        logger.info("Best parameters found: %s", search_result.best_params)

        logger.info("Topic modeling finished.")

    def _generate_run_id(self, model_name: str, strategy: str) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return f"{model_name.lower()}_{strategy}_{ts}"
