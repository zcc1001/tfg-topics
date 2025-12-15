from abc import ABC, abstractmethod
from typing import List

from ingestion.src.domain.entities.entities import RepositoryInfo


class RepoListReaderPort(ABC):
    @abstractmethod
    def fetch_repo_list(self) -> List[RepositoryInfo]:
        raise NotImplementedError
