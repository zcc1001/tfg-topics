import itertools
from typing import Callable, List, TypeVar

from ingestion.application.ports.github_port import GitHubPort
from ingestion.application.ports.repo_list_reader import RepoListReaderPort
from ingestion.application.ports.storage_port import StoragePort

T = TypeVar("T")


class DataIngestionUsecase:
    """A class method to ingesting data from GitHub and persisting repository data."""

    def __init__(
        self,
        github_port: GitHubPort,
        repo_info_reader: RepoListReaderPort,
        storage_port: StoragePort,
    ):
        self.github_port = github_port
        self.repo_info_reader = repo_info_reader
        self.storage = storage_port

    def _process_repos(self, data_fetcher_func: Callable[[str, str], T]) -> List[T]:
        repos_info = self.repo_info_reader.fetch_repo_list()
        all_data = []
        for repo_info in repos_info:
            owner, repo_name = repo_info.owner, repo_info.name
            data = data_fetcher_func(owner, repo_name)
            all_data.append(data)
        return all_data

    def ingest_issues_data(self) -> None:
        """Pull all issues from the API."""
        all_repos_issues = self._process_repos(
            lambda owner, name: self.github_port.get_issues(owner=owner, repo_name=name)
        )
        issue_list = list(itertools.chain.from_iterable(all_repos_issues))
        self.storage.save_issue(issue_list)

    def ingest_readme_data(self) -> None:
        """Pull all readmes from the API."""
        all_repos_readme = self._process_repos(
            lambda owner, name: self.github_port.get_readme(owner=owner, repo_name=name)
        )

        valid_readmes = [readme for readme in all_repos_readme if readme is not None]
        self.storage.save_readme(valid_readmes)

    def ingest_thesis_data(self) -> None:
        """Pull all thesis data from the API."""
        all_repos_thesis_data = self._process_repos(
            lambda owner, name: self.github_port.get_thesis_data(
                owner=owner, repo_name=name
            )
        )

        valid_thesis_data = [
            thesis for thesis in all_repos_thesis_data if thesis is not None
        ]
        self.storage.save_thesis_data(valid_thesis_data)
