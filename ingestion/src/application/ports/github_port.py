from abc import ABC, abstractmethod
from typing import List

from domain.entities.entities import IssueData, ReadmeData


class GitHubPort(ABC):
    @abstractmethod
    def get_issues(self, owner: str, repo_name: str) -> List[IssueData]:
        raise NotImplementedError

    @abstractmethod
    def get_readme(self, owner: str, repo_name: str) -> ReadmeData:
        raise NotImplementedError
