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

    def load_thesis_metadata(
        self,
    ) -> Optional[pd.DataFrame]:
        return self._safe_read(self._path("metadata"))
