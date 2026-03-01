from typing import Any, Dict, List

from processing.application.ports.document_repository import DocumentRepository
from processing.application.ports.storage_port import StoragePort
from processing.application.ports.topic_model_port import TopicModelPort
from processing.application.services.hyperparam_service import (
    HyperparameterSearchService,
)
from processing.application.usecases.topic_modeling_usecase import TopicModelingUseCase
from processing.domain.entities import (
    Document,
    HyperparameterSearchResult,
    TopicModelResult,
)


class _DummyDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self.requested_name: str | None = None

    def load_documents(self, doc_name: str) -> List[Document]:
        self.requested_name = doc_name
        return [Document(text="doc a"), Document(text="doc b")]


class _DummyHyperparamService(HyperparameterSearchService):
    def __init__(self, result: HyperparameterSearchResult) -> None:
        self.result = result
        self.called_with: Dict[str, Any] | None = None

    def search(self, dataset: str, model_wrapper: Any, texts: List[str]) -> Any:
        self.called_with = {
            "dataset": dataset,
            "model_wrapper": model_wrapper,
            "texts": texts,
        }
        return self.result


class _DummyModelAdapter(TopicModelPort):
    def __init__(self, topic_result: TopicModelResult) -> None:
        self.topic_result = topic_result
        self.fit_called_with: Dict[str, Any] | None = None

    def fit(
        self,
        dataset: str,
        texts: List[str],
        params: Dict[str, Any],
        dataset_hash: str,
    ) -> TopicModelResult:
        self.fit_called_with = {
            "dataset": dataset,
            "texts": texts,
            "params": params,
            "dataset_hash": dataset_hash,
        }
        return self.topic_result

    def suggest_params(self, _trial: Any) -> Dict[str, Any]:
        return {}

    def train_and_evaluate(self, _texts: List[str], _params: Dict[str, Any]) -> float:
        return 0.0

    def model_name(self) -> str:
        return "dummy"


class _DummyWriter(StoragePort):
    def __init__(self) -> None:
        self.hyper_written: HyperparameterSearchResult | None = None
        self.topic_written: TopicModelResult | None = None
        self.run_id: str | None = None

    def write_hyperparameter_search(self, result: HyperparameterSearchResult) -> None:
        self.hyper_written = result

    def write_topic_model_result(
        self, run_id: str, result: TopicModelResult
    ) -> None:  # noqa: D401
        self.topic_written = result
        self.run_id = run_id


def test_execute_runs_search_and_training_and_writes_results() -> None:
    """Execute should run hyperparameter search, fit the model and persist results."""
    # prepare results to be returned by the stubbed services
    hyper_result = HyperparameterSearchResult(
        model_name="dummy",
        dataset="issues",
        best_params={"k": 3},
        best_score=0.9,
        trials=[],
    )

    topic_result = TopicModelResult(
        dataset="issues",
        model_name="dummy",
        topics={0: ["a", "b"]},
        document_topics=[{"doc": 0}],
        metrics={"coherence": 0.5},
        params={"k": 3},
        topic_coordinates=[],
        runtime_seconds=1.0,
        dataset_hash="hash-123",
    )

    repo = _DummyDocumentRepository()
    hyper_service = _DummyHyperparamService(result=hyper_result)
    model_adapter = _DummyModelAdapter(topic_result=topic_result)
    writer = _DummyWriter()

    class _TestableTopicModelingUseCase(TopicModelingUseCase):
        def _generate_run_id(self, model_name: str, strategy: str) -> str:
            return "dummy_run_id"

    usecase = _TestableTopicModelingUseCase(
        document_repository=repo,
        hyperparam_service=hyper_service,
        model_adapter=model_adapter,
        writer=writer,
        dataset_hash="hash-123",
    )
    # run
    usecase.execute(dataset="issues")

    # repository should be asked for the parquet file
    assert repo.requested_name == "issues.parquet"

    # hyperparameter search should be invoked with the model adapter and texts
    assert hyper_service.called_with is not None
    assert hyper_service.called_with["dataset"] == "issues"
    assert isinstance(hyper_service.called_with["model_wrapper"], _DummyModelAdapter)
    assert hyper_service.called_with["texts"] == ["doc a", "doc b"]

    # model fit should be called with the best params returned by the search
    assert model_adapter.fit_called_with is not None
    assert model_adapter.fit_called_with["dataset"] == "issues"
    assert model_adapter.fit_called_with["params"] == {"k": 3}
    assert model_adapter.fit_called_with["dataset_hash"] == "hash-123"

    # writer should have been called for both search and final result
    assert writer.hyper_written is hyper_result
    assert writer.topic_written is topic_result
    assert writer.run_id == "dummy_run_id"


def test_execute_with_abstracts_uses_abstracts_parquet() -> None:
    hyper_result = HyperparameterSearchResult(
        model_name="dummy",
        dataset="abstracts",
        best_params={"k": 2},
        best_score=0.7,
        trials=[],
    )

    topic_result = TopicModelResult(
        dataset="abstracts",
        model_name="dummy",
        topics={0: ["abstract", "topic"]},
        document_topics=[{"document_id": 0, "topic_id": 0, "probability": 0.9}],
        metrics={"coherence": 0.4},
        params={"k": 2},
        topic_coordinates=[],
        runtime_seconds=1.0,
        dataset_hash="hash-456",
    )

    repo = _DummyDocumentRepository()
    hyper_service = _DummyHyperparamService(result=hyper_result)
    model_adapter = _DummyModelAdapter(topic_result=topic_result)
    writer = _DummyWriter()

    class _TestableTopicModelingUseCase(TopicModelingUseCase):
        def _generate_run_id(self, model_name: str, strategy: str) -> str:
            return "dummy_run_id"

    usecase = _TestableTopicModelingUseCase(
        document_repository=repo,
        hyperparam_service=hyper_service,
        model_adapter=model_adapter,
        writer=writer,
        dataset_hash="hash-456",
    )

    usecase.execute(dataset="abstracts")

    assert repo.requested_name == "abstracts.parquet"
    assert hyper_service.called_with is not None
    assert hyper_service.called_with["dataset"] == "abstracts"
    assert model_adapter.fit_called_with is not None
    assert model_adapter.fit_called_with["dataset"] == "abstracts"
    assert writer.topic_written is topic_result
