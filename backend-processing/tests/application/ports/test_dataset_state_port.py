import inspect

import pytest

from processing.application.ports.dataset_state_port import DatasetStatePort


class DummyDatasetStatePort(DatasetStatePort):
    def read_current_dataset_hash(self, dataset: str) -> str:
        raise NotImplementedError

    def read_last_processed_hash(self, dataset: str, model_name: str) -> str | None:
        raise NotImplementedError

    def invalidate_model_results(self, dataset: str, model_name: str) -> None:
        raise NotImplementedError

    def invalidate_mismatched_results(self, dataset: str, current_hash: str) -> None:
        raise NotImplementedError


def test_dataset_state_port_cannot_be_instantiated() -> None:
    assert inspect.isabstract(DatasetStatePort)


def test_dataset_state_port_methods_raise_not_implemented() -> None:
    port = DummyDatasetStatePort()

    with pytest.raises(NotImplementedError):
        port.read_current_dataset_hash("test")

    with pytest.raises(NotImplementedError):
        port.read_last_processed_hash("test", "model")

    with pytest.raises(NotImplementedError):
        port.invalidate_model_results("test", "model")

    with pytest.raises(NotImplementedError):
        port.invalidate_mismatched_results("test", "hash")
