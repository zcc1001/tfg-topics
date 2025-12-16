from abc import ABC, abstractmethod
from typing import List

from domain.entities.entities import RepositoryInfo


class RepoListReaderPort(ABC):
    @abstractmethod
    def fetch_repo_list(self) -> List[RepositoryInfo]:
        raise NotImplementedError
