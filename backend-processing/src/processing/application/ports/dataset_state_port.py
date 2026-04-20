from abc import ABC, abstractmethod


class DatasetStatePort(ABC):
    """Abstract port for reading processing dataset state."""

    @abstractmethod
    def read_current_dataset_hash(self, dataset: str) -> str:
        """Return the current content hash for the requested dataset."""
        raise NotImplementedError

    @abstractmethod
    def read_last_processed_hash(self, dataset: str, model_name: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def invalidate_model_results(self, dataset: str, model_name: str) -> None:
        """Invalidate any stored model result.

        Implementations should remove or mark the stored hash as invalid so
        that subsequent runs treat the dataset as changed.
        """
        raise NotImplementedError

    @abstractmethod
    def invalidate_mismatched_results(self, dataset: str, current_hash: str) -> None:
        """Invalidate model results whose stored dataset hash mismatches.

        Implementations should scan existing model outputs and remove
        those that do not match the current dataset hash.
        """
        raise NotImplementedError
