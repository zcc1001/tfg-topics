from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd


class MetadataRepository(ABC):

    @abstractmethod
    def load_dataset_metadata(self, dataset: str) -> Optional[pd.DataFrame]:
        """
        Load metadata for a dataset, including optional enrichment fields such as
        title, tutor, year or grade when available.

        Returns:
            A pandas DataFrame with dataset metadata.
        """
        raise NotImplementedError
