import itertools

from ingestion.src.application.ports.github_port import GitHubPort
from ingestion.src.application.ports.repo_list_reader import RepoListReaderPort
from ingestion.src.application.ports.storage_port import StoragePort


class DataIngestionUsecase():
    def __init__(self, github_port: GitHubPort, repo_info_reader: RepoListReaderPort, storage_port: StoragePort):
        self.github_port = github_port
        self.repo_info_reader = repo_info_reader
        self.storage = storage_port

    def _process_repos(self, data_fetcher_func):
        repos_info = self.repo_info_reader.fetch_repo_list()
        all_data = []
        for repo_info in repos_info:
            owner, repo_name = repo_info.owner, repo_info.name
            data = data_fetcher_func(owner, repo_name)
            all_data.append(data)
        return all_data

    def ingest_issues_data(self):
        all_repos_issues = self._process_repos(
            lambda owner, name: self.github_port.get_issues(owner=owner, repo_name=name)
        )
        issue_list = list(itertools.chain.from_iterable(all_repos_issues))
        self.storage.save_issue(issue_list)

    def ingest_readme_data(self):
        all_repos_readme = self._process_repos(
            lambda owner, name: self.github_port.get_readme(owner=owner, repo_name=name)
        )

        valid_readmes = [readme for readme in all_repos_readme if readme is not None]
        self.storage.save_readme(valid_readmes)
