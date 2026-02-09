from abc import ABC, abstractmethod


class DatasetStatePort(ABC):
    """Abstract port for reading and writing dataset state.

    The port exposes a minimal contract required by the ingestion
    application to detect dataset changes and invalidate cached or derived
    artifacts when the dataset contents change.
    """

    @abstractmethod
    def read_dataset_hash(self) -> str | None:
        """Return the previously stored dataset hash.

        Returns:
            The dataset hash as a string if present, otherwise ``None``.
        """
        raise NotImplementedError

    @abstractmethod
    def write_dataset_hash(self, dataset_hash: str) -> None:
        """Persist the provided dataset hash.

        Args:
            dataset_hash: A string representing the dataset content hash.
        """
        raise NotImplementedError

    @abstractmethod
    def invalidate_dataset(self) -> None:
        """Invalidate any stored dataset state.

        Implementations should remove or mark the stored hash as invalid so
        that subsequent runs treat the dataset as changed.
        """
        raise NotImplementedError
