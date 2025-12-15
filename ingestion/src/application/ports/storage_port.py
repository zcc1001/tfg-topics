from abc import ABC, abstractmethod
from typing import List

from ingestion.src.domain.entities.entities import ReadmeData, IssueData


class StoragePort(ABC):
    @abstractmethod
    def save_issue(self, issue_data: List[IssueData]) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_readme(self, readme_data: List[ReadmeData]) -> None:
        raise NotImplementedError
