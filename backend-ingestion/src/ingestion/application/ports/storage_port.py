from abc import ABC, abstractmethod
from typing import List

from ingestion.domain.entities.entities import IssueData, ReadmeData, ThesisData


class StoragePort(ABC):
    @abstractmethod
    def save_issue(self, issue_data: List[IssueData]) -> None:
        """Save the issue data to the server .

        Args:
            issue_data (List[IssueData]): list of issue data objects

        Raises:
            NotImplementedError: not implemented error
        """
        raise NotImplementedError

    @abstractmethod
    def save_readme(self, readme_data: List[ReadmeData]) -> None:
        """Save the readme data to the file .

        Args:
            readme_data (List[ReadmeData]): list of readme data objects

        Raises:
            NotImplementedError: not implemented error
        """
        raise NotImplementedError

    @abstractmethod
    def save_thesis_data(self, thesis_data: List[ThesisData]) -> None:
        """Save the thesis data to the file .
        Args:
            thesis_data (List[ThesisData]): list of thesis data objects
        Raises:
            NotImplementedError: not implemented error
        """
        raise NotImplementedError
