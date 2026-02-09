from abc import ABC, abstractmethod
from typing import List

from ingestion.domain.entities.entities import ThesisInfo


class RepoListReaderPort(ABC):
    @abstractmethod
    def fetch_repo_list(self) -> List[ThesisInfo]:
        """Fetches the list of all the repositories in the device .

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.

        Returns:
            List[RepositoryInfo]: A list of RepositoryInfo entities
        """
        raise NotImplementedError
