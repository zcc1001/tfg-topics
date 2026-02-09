import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from processing.application.ports.document_repository import DocumentRepository
from processing.application.ports.storage_port import StoragePort
from processing.application.ports.topic_model_port import TopicModelPort
from processing.application.services.hyperparam_service import (
    HyperparameterSearchService,
)
from processing.domain.entities import Document

logger = logging.getLogger(__name__)


class TopicModelingUseCase:
    """Topic modeling use case."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        hyperparam_service: HyperparameterSearchService,
        model_adapter: TopicModelPort,
        writer: StoragePort,
        dataset_hash: str,
    ):
        self.document_repository = document_repository
        self.hyperparam_service = hyperparam_service
        self.model_adapter = model_adapter
        self.writer = writer
        self.dataset_hash = dataset_hash

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
            dataset=dataset,
            texts=texts,
            params=search_result.best_params,
            dataset_hash=self.dataset_hash,
        )

        topic_result.document_topics = self._attach_document_metadata(
            document_topics=topic_result.document_topics,
            documents=documents,
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

    def _attach_document_metadata(
        self,
        document_topics: List[Dict[str, Any]],
        documents: List[Document],
    ) -> List[Dict[str, Any]]:
        if not document_topics or not documents:
            return document_topics

        metadata_by_id: Dict[int, Dict[str, Any]] = {}
        for idx, doc in enumerate(documents):
            if doc.metadata:
                metadata_by_id[idx] = doc.metadata

        if not metadata_by_id:
            return document_topics

        enriched: List[Dict[str, Any]] = []
        for row in document_topics:
            doc_id = row.get("document_id")
            doc_index: int | None = None
            if doc_id is not None:
                try:
                    doc_index = int(doc_id)
                except (TypeError, ValueError):
                    pass

            if doc_index is not None:
                metadata = metadata_by_id.get(doc_index, {})
            else:
                metadata = {}

            if metadata:
                enriched.append({**row, **self._flatten_metadata(metadata)})
            else:
                enriched.append(row)

        return enriched

    def _flatten_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {f"meta_{key}": value for key, value in metadata.items()}
