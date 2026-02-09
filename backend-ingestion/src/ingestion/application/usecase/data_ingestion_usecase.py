import itertools
from typing import TypeVar

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

    def ingest_issues_data(self) -> None:
        """Pull all issues from the API."""
        all_repos_issues = []
        repos_info = self.repo_info_reader.fetch_repo_list()
        for repo_info in repos_info:
            owner, repo_name = repo_info.repo_owner, repo_info.repo_name
            data = self.github_port.get_issues(owner=owner, repo_name=repo_name)
            for issue in data:
                issue.thesis_id = repo_info.thesis_id
            if data:
                all_repos_issues.append(data)

        issue_list = list(itertools.chain.from_iterable(all_repos_issues))
        self.storage.save_issue(issue_list)

    def ingest_readme_data(self) -> None:
        """Pull all readmes from the API."""
        repos_info = self.repo_info_reader.fetch_repo_list()
        all_repos_readme_data = []

        for repo_info in repos_info:
            readme_data = self.github_port.get_readme(
                owner=repo_info.repo_owner,
                repo_name=repo_info.repo_name,
            )
            if readme_data:
                readme_data.thesis_id = repo_info.thesis_id
                all_repos_readme_data.append(readme_data)

        valid_readmes = [
            readme for readme in all_repos_readme_data if readme is not None
        ]
        self.storage.save_readme(valid_readmes)

    def ingest_thesis_data(self) -> None:
        """Pull all thesis data from the API."""
        repos_info = self.repo_info_reader.fetch_repo_list()
        all_repos_thesis_data = []

        for repo_info in repos_info:
            thesis = self.github_port.get_thesis_data(
                owner=repo_info.repo_owner,
                repo_name=repo_info.repo_name,
            )
            if thesis:
                thesis.thesis_id = repo_info.thesis_id
                all_repos_thesis_data.append(thesis)

        valid_thesis_data = [
            thesis for thesis in all_repos_thesis_data if thesis is not None
        ]
        self.storage.save_thesis_data(valid_thesis_data)

    def ingest_thesis_metadata(self) -> None:
        """
        Persist academic thesis metadata extracted from the CSV.
        This should be executed once per ingestion run.
        """
        thesis_infos = self.repo_info_reader.fetch_repo_list()
        self.storage.save_thesis_metadata(thesis_infos)
