from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd


class MetadataRepository(ABC):

    @abstractmethod
    def load_thesis_metadata(
        self,
    ) -> Optional[pd.DataFrame]:
        """
        Load the metadata for the theses, including fields like tutor, year, etc.

        Returns:
            A pandas DataFrame with the hyperparameter trials.
        """
        raise NotImplementedError
