from datetime import datetime, timezone

from ingestion.application.ports.github_port import GitHubPort
from ingestion.application.ports.repo_list_reader import RepoListReaderPort
from ingestion.application.ports.storage_port import StoragePort
from ingestion.application.usecase.data_ingestion_usecase import DataIngestionUsecase
from ingestion.domain.entities.entities import (
    IssueData,
    ReadmeData,
    TextData,
    ThesisData,
    ThesisInfo,
)


class DummyRepoReader(RepoListReaderPort):
    def __init__(self, repos: list[ThesisInfo]) -> None:
        self._repos = repos

    def fetch_repo_list(self) -> list[ThesisInfo]:
        return self._repos


class DummyGitHubPort(GitHubPort):
    def __init__(
        self,
        issues_map: dict[tuple[str, str], list[IssueData]] | None = None,
        readme_map: dict[tuple[str, str], ReadmeData | None] | None = None,
        thesis_map: dict[tuple[str, str], ThesisData | None] | None = None,
    ) -> None:
        self.issues_map = issues_map or {}
        self.readme_map = readme_map or {}
        self.thesis_map = thesis_map or {}

    def get_issues(self, owner: str, repo_name: str) -> list[IssueData]:
        return self.issues_map.get((owner, repo_name), [])

    def get_readme(self, owner: str, repo_name: str) -> ReadmeData | None:
        return self.readme_map.get((owner, repo_name))

    def get_thesis_data(self, owner: str, repo_name: str) -> ThesisData | None:
        return self.thesis_map.get((owner, repo_name))


class DummyStorage(StoragePort):
    def __init__(self) -> None:
        self.saved_issues: list | None = None
        self.saved_readmes: list | None = None
        self.saved_thesis: list | None = None
        self.saved_metadata: list | None = None

    def save_issue(self, issue_data: list[IssueData]) -> None:
        self.saved_issues = issue_data

    def save_readme(self, readme_data: list[ReadmeData]) -> None:
        self.saved_readmes = readme_data

    def save_thesis_data(self, thesis_data: list[ThesisData]) -> None:
        self.saved_thesis = thesis_data

    def save_thesis_metadata(self, thesis_metadata: list[ThesisInfo]) -> None:
        self.saved_metadata = thesis_metadata


def _make_thesis_info(repo_name: str, repo_owner: str, thesis_id: int) -> ThesisInfo:
    return ThesisInfo(
        thesis_id=thesis_id,
        title=f"Title {thesis_id}",
        tutor="Tutor",
        student="Student",
        presentation_date="2023-01-01",
        assignment_date="2022-01-01",
        grade="10",
        repository_url=f"https://github.com/{repo_owner}/{repo_name}",
        repo_owner=repo_owner,
        repo_name=repo_name,
    )


def test_ingest_issues_data_flattens_and_saves() -> None:
    """Ensure issues from multiple repositories are flattened and saved.

    The usecase should collect issues for each repository, flatten the
    nested lists and pass the combined list to the storage port.
    """

    repos = [
        _make_thesis_info(repo_name="r1", repo_owner="o1", thesis_id=1),
        _make_thesis_info(repo_name="r2", repo_owner="o2", thesis_id=2),
    ]

    issues_map = {
        ("o1", "r1"): [
            IssueData(1, "o1", "r1", 1, "t1", "d1", datetime.now(timezone.utc)),
        ],
        ("o2", "r2"): [
            IssueData(2, "o2", "r2", 2, "t2", "d2", datetime.now(timezone.utc)),
            IssueData(2, "o2", "r2", 3, "t3", "d3", datetime.now(timezone.utc)),
        ],
    }

    github = DummyGitHubPort(issues_map=issues_map)
    reader = DummyRepoReader(repos)
    storage = DummyStorage()

    u = DataIngestionUsecase(github, reader, storage)
    u.ingest_issues_data()

    assert storage.saved_issues is not None
    assert len(storage.saved_issues) == 3


def test_ingest_readme_data_filters_none_and_saves() -> None:
    """Ensure only non-None readmes are saved by the storage port."""

    repos = [
        _make_thesis_info(repo_name="r1", repo_owner="o1", thesis_id=1),
        _make_thesis_info(repo_name="r2", repo_owner="o2", thesis_id=2),
    ]

    readme_map = {
        ("o1", "r1"): ReadmeData(1, "url", "content", datetime.now(timezone.utc)),
        ("o2", "r2"): None,
    }

    github = DummyGitHubPort(readme_map=readme_map)
    reader = DummyRepoReader(repos)
    storage = DummyStorage()

    u = DataIngestionUsecase(github, reader, storage)
    u.ingest_readme_data()

    assert storage.saved_readmes is not None
    assert len(storage.saved_readmes) == 1
    assert storage.saved_readmes[0].thesis_id == 1


def test_ingest_thesis_data_filters_none_and_saves() -> None:
    """Ensure only non-None thesis data are saved by the storage port."""

    repos = [
        _make_thesis_info(repo_name="r1", repo_owner="o1", thesis_id=1),
        _make_thesis_info(repo_name="r2", repo_owner="o2", thesis_id=2),
    ]

    thesis_map = {
        ("o1", "r1"): ThesisData(1, [TextData("x", "s")], datetime.now(timezone.utc)),
        ("o2", "r2"): None,
    }

    github = DummyGitHubPort(thesis_map=thesis_map)
    reader = DummyRepoReader(repos)
    storage = DummyStorage()

    u = DataIngestionUsecase(github, reader, storage)
    u.ingest_thesis_data()

    assert storage.saved_thesis is not None
    assert len(storage.saved_thesis) == 1
    assert storage.saved_thesis[0].thesis_id == 1
