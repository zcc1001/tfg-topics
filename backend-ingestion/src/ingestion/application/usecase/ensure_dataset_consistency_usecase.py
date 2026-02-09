import hashlib
import logging
from pathlib import Path

from ingestion.application.ports.dataset_state_port import DatasetStatePort

logger = logging.getLogger(__name__)


class EnsureDatasetConsistencyUseCase:
    """
    Ensures that ingestion outputs are consistent with the current dataset CSV.
    """

    def __init__(self, dataset_state_port: DatasetStatePort):
        self._state = dataset_state_port

    def execute(self, csv_path: str) -> None:
        current_hash = self._compute_hash(csv_path)
        stored_hash = self._state.read_dataset_hash()

        if stored_hash is None:
            logger.info(
                "No stored dataset hash found. Storing current hash for"
                " future consistency checks."
            )
            self._state.write_dataset_hash(current_hash)
            return

        if stored_hash != current_hash:
            self._state.invalidate_dataset()
            self._state.write_dataset_hash(current_hash)

    @staticmethod
    def _compute_hash(path: str) -> str:
        hasher = hashlib.sha256()
        with Path(path).open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
