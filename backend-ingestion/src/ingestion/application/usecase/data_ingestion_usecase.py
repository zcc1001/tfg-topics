import itertools

from ingestion.application.ports.github_port import GitHubPort
from ingestion.application.ports.repo_list_reader import RepoListReaderPort
from ingestion.application.ports.storage_port import StoragePort
from ingestion.domain.entities.entities import ThesisInfo
from ingestion.domain.entities.ingestion_summary import IngestionSummary


class DataIngestionUsecase:
    """Ingest data from GitHub and persist repository data."""

    def __init__(
        self,
        github_port: GitHubPort,
        repo_info_reader: RepoListReaderPort,
        storage_port: StoragePort,
    ) -> None:
        self.github_port = github_port
        self.repo_info_reader = repo_info_reader
        self.storage = storage_port

    def ingest_issues_data(self) -> IngestionSummary:
        """Pull all issues from the API."""
        all_repos_issues = []
        repos_info = self.repo_info_reader.fetch_repo_list()
        repos_with_data: list[str] = []
        repos_without_data: list[str] = []
        repo_record_counts: dict[str, int] = {}
        for repo_info in repos_info:
            owner, repo_name = repo_info.repo_owner, repo_info.repo_name
            repo_full_name = self._repo_full_name(repo_info)
            data = self.github_port.get_issues(owner=owner, repo_name=repo_name)
            for issue in data:
                issue.thesis_id = repo_info.thesis_id
            if data:
                all_repos_issues.append(data)
                repos_with_data.append(repo_full_name)
                repo_record_counts[repo_full_name] = len(data)
            else:
                repos_without_data.append(repo_full_name)

        issue_list = list(itertools.chain.from_iterable(all_repos_issues))
        self.storage.save_issue(issue_list)
        return IngestionSummary(
            data_type="issues",
            repos_with_data=repos_with_data,
            repos_without_data=repos_without_data,
            with_data_count=len(repos_with_data),
            without_data_count=len(repos_without_data),
            repo_record_counts=repo_record_counts,
        )

    def ingest_readme_data(self) -> IngestionSummary:
        """Pull all readmes from the API."""
        repos_info = self.repo_info_reader.fetch_repo_list()
        all_repos_readme_data = []
        repos_with_data: list[str] = []
        repos_without_data: list[str] = []
        repo_record_counts: dict[str, int] = {}

        for repo_info in repos_info:
            repo_full_name = self._repo_full_name(repo_info)
            readme_data = self.github_port.get_readme(
                owner=repo_info.repo_owner,
                repo_name=repo_info.repo_name,
            )
            if readme_data:
                readme_data.thesis_id = repo_info.thesis_id
                all_repos_readme_data.append(readme_data)
                repos_with_data.append(repo_full_name)
                repo_record_counts[repo_full_name] = 1
            else:
                repos_without_data.append(repo_full_name)

        self.storage.save_readme(all_repos_readme_data)
        return IngestionSummary(
            data_type="readmes",
            repos_with_data=repos_with_data,
            repos_without_data=repos_without_data,
            with_data_count=len(repos_with_data),
            without_data_count=len(repos_without_data),
            repo_record_counts=repo_record_counts,
        )

    def ingest_thesis_data(self) -> IngestionSummary:
        """Pull all thesis data from the API."""
        repos_info = self.repo_info_reader.fetch_repo_list()
        all_repos_thesis_data = []
        repos_with_data: list[str] = []
        repos_without_data: list[str] = []
        repo_record_counts: dict[str, int] = {}

        for repo_info in repos_info:
            repo_full_name = self._repo_full_name(repo_info)
            thesis = self.github_port.get_thesis_data(
                owner=repo_info.repo_owner,
                repo_name=repo_info.repo_name,
            )
            if thesis:
                thesis.thesis_id = repo_info.thesis_id
                all_repos_thesis_data.append(thesis)
                repos_with_data.append(repo_full_name)
                repo_record_counts[repo_full_name] = len(thesis.texts)
            else:
                repos_without_data.append(repo_full_name)

        self.storage.save_thesis_data(all_repos_thesis_data)
        return IngestionSummary(
            data_type="thesis",
            repos_with_data=repos_with_data,
            repos_without_data=repos_without_data,
            with_data_count=len(repos_with_data),
            without_data_count=len(repos_without_data),
            repo_record_counts=repo_record_counts,
        )

    def ingest_thesis_metadata(self) -> None:
        """
        Persist academic thesis metadata extracted from the CSV.
        This should be executed once per ingestion run.
        """
        thesis_infos = self.repo_info_reader.fetch_repo_list()
        self.storage.save_thesis_metadata(thesis_infos)

    def ingest_abstracts_data(self) -> IngestionSummary:
        """Pull all abstracts data from the API."""
        repos_info = self.repo_info_reader.fetch_repo_list()
        all_repos_abstracts_data = []
        repos_with_data: list[str] = []
        repos_without_data: list[str] = []
        repo_record_counts: dict[str, int] = {}

        for repo_info in repos_info:
            repo_full_name = self._repo_full_name(repo_info)
            abstracts = self.github_port.get_abstracts_data(
                owner=repo_info.repo_owner,
                repo_name=repo_info.repo_name,
            )
            if abstracts:
                abstracts.thesis_id = repo_info.thesis_id
                all_repos_abstracts_data.append(abstracts)
                repos_with_data.append(repo_full_name)
                repo_record_counts[repo_full_name] = 1
            else:
                repos_without_data.append(repo_full_name)

        self.storage.save_abstracts_data(all_repos_abstracts_data)
        return IngestionSummary(
            data_type="abstracts",
            repos_with_data=repos_with_data,
            repos_without_data=repos_without_data,
            with_data_count=len(repos_with_data),
            without_data_count=len(repos_without_data),
            repo_record_counts=repo_record_counts,
        )

    @staticmethod
    def _repo_full_name(repo_info: ThesisInfo) -> str:
        return f"{repo_info.repo_owner}/{repo_info.repo_name}"
