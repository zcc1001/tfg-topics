from abc import ABC, abstractmethod
from typing import List, Optional

from ingestion.domain.entities.entities import IssueData, ReadmeData, ThesisData


class GitHubPort(ABC):
    @abstractmethod
    def get_issues(self, owner: str, repo_name: str) -> List[IssueData]:
        """Returns the list of issues for the given repository .

        Args:
            owner (str): owner of the repository
            repo_name (str): repository name

        Raises:
            NotImplementedError: not implemented error

        Returns:
            List[IssueData]: list of issue data objects
        """
        raise NotImplementedError

    @abstractmethod
    def get_readme(self, owner: str, repo_name: str) -> Optional[ReadmeData]:
        """Returns readme information for a given repository .

        Args:
            owner (str): owner of the repository
            repo_name (str): repository name

        Raises:
            NotImplementedError: not implemented error

        Returns:
            ReadmeData: readme data object
        """
        raise NotImplementedError

    @abstractmethod
    def get_thesis_data(self, owner: str, repo_name: str) -> Optional[ThesisData]:
        """Get the thesis data for the repository .

        Args:
            owner (str): owner of the repository
            repo_name (str): repository nam

        Raises:
            NotImplementedError: not implemented error

        Returns:
            ThesisData: thesis data object
        """
        raise NotImplementedError
