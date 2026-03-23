import os
from typing import Optional

import pandas as pd

from webapp.application.ports.metadata_repository import MetadataRepository


class MetadataParquetRepository(MetadataRepository):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def _path(self, suffix: str) -> str:
        return os.path.join(self.base_path, f"{suffix}.parquet")

    def _safe_read(self, path: str) -> Optional[pd.DataFrame]:
        if not os.path.exists(path):
            return None
        return pd.read_parquet(path)

    def load_dataset_metadata(self, dataset: str) -> Optional[pd.DataFrame]:
        metadata = self._safe_read(self._path("metadata"))
        if metadata is not None and not metadata.empty:
            return metadata

        return self._safe_read(self._path(dataset))
