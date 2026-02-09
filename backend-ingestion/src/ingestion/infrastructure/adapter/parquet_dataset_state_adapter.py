import logging
import os

from ingestion.application.ports.dataset_state_port import DatasetStatePort

logger = logging.getLogger(__name__)


class ParquetDatasetStateAdapter(DatasetStatePort):
    def __init__(self, ingestion_dir: str):
        self._hash_path = os.path.join(ingestion_dir, "dataset_version.txt")
        self._ingestion_dir = ingestion_dir

    def read_dataset_hash(self) -> str | None:
        if not os.path.exists(self._hash_path):
            return None
        with open(self._hash_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def write_dataset_hash(self, dataset_hash: str) -> None:
        with open(self._hash_path, "w", encoding="utf-8") as f:
            f.write(dataset_hash)

    def invalidate_dataset(self) -> None:
        logger.warning("Invalidating ingestion dataset due to CSV change")

        for filename in os.listdir(self._ingestion_dir):
            if filename.endswith(".parquet"):
                os.remove(os.path.join(self._ingestion_dir, filename))
                logger.info("Deleted %s", filename)
