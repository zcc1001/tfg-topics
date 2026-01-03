import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pandas as pd
import pytest

from ingestion.domain.entities.entities import (
    IssueData,
    ReadmeData,
    TextData,
    ThesisData,
)
from ingestion.infrastructure.adapter.ingestion_parquet_storage import (
    IngestionParquetStorage,
)


@pytest.fixture
def issue_data_factory() -> Callable[[int], list[IssueData]]:
    """Fixture that returns a factory for creating IssueData objects."""

    def _factory(count: int = 1) -> list[IssueData]:
        return [
            IssueData(
                repo_name=f"repo{i}",
                repo_owner="owner",
                issue_id=i,
                title=f"Issue {i}",
                description=f"Description {i}",
                retrieved_at=datetime.now(timezone.utc),
            )
            for i in range(count)
        ]

    return _factory


@pytest.fixture
def readme_data_factory() -> Callable[[int], list[ReadmeData]]:
    """Fixture that returns a factory for creating ReadmeData objects."""

    def _factory(count: int = 1) -> list[ReadmeData]:  # type: ignore
        return [
            ReadmeData(
                repo_name=f"repo{i}",
                repo_owner="owner",
                download_url=f"http://example.com/{i}",
                content=f"content {i}",
                retrieved_at=datetime.now(timezone.utc),
            )
            for i in range(count)
        ]

    return _factory


@pytest.fixture
def thesis_data_factory() -> Callable[[int], list[ThesisData]]:
    """Fixture that returns a factory for creating ThesisData objects."""

    def _factory(count: int = 1) -> list[ThesisData]:
        return [
            ThesisData(
                repo_name=f"repo{i}",
                repo_owner="owner",
                texts=[TextData(contents=f"text {i}", section=f"section {i}")],
                retrieved_at=datetime.now(timezone.utc),
            )
            for i in range(count)
        ]

    return _factory


def test_save_issue(
    tmp_path: Path, issue_data_factory: Callable[[int], list[IssueData]]
) -> None:
    """Save multiple issues to parquet and verify they were written."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    issues = issue_data_factory(2)

    storage.save_issue(issues)

    df = pd.read_parquet(storage.issues_path)
    assert len(df) == 2
    assert df["issue_id"].tolist() == [0, 1]


def test_save_issue_append(
    tmp_path: Path, issue_data_factory: Callable[[int], list[IssueData]]
) -> None:
    """Append new issues and ensure the file contains both entries."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path), buffer_size=1)
    issues1 = issue_data_factory(1)
    storage.save_issue(issues1)

    df1 = pd.read_parquet(storage.issues_path)
    assert len(df1) == 1

    issues2 = issue_data_factory(2)[1:]  # Create a second, different issue
    storage.save_issue(issues2)

    df2 = pd.read_parquet(storage.issues_path)
    assert len(df2) == 2
    assert df2["issue_id"].tolist() == [0, 1]


def test_save_readme(
    tmp_path: Path, readme_data_factory: Callable[[int], list[ReadmeData]]
) -> None:
    """Save readme entries to parquet and assert they are present."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    readmes = readme_data_factory(2)

    storage.save_readme(readmes)

    df = pd.read_parquet(storage.readmes_path)
    assert len(df) == 2
    assert df["repo_name"].tolist() == ["repo0", "repo1"]


def test_save_thesis_data(
    tmp_path: Path, thesis_data_factory: Callable[[int], list[ThesisData]]
) -> None:
    """Persist thesis extracted texts and validate structure in parquet."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    thesis_data = thesis_data_factory(2)

    storage.save_thesis_data(thesis_data)

    df = pd.read_parquet(storage.thesis_path)
    assert len(df) == 2
    assert df["repo_name"].tolist() == ["repo0", "repo1"]
    assert len(df["texts"][0]) == 1


def test_save_empty_lists(tmp_path: Path) -> None:
    """Saving empty lists should not create output files."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    storage.save_issue([])
    storage.save_readme([])
    storage.save_thesis_data([])

    assert not os.path.exists(storage.issues_path)
    assert not os.path.exists(storage.readmes_path)
    assert not os.path.exists(storage.thesis_path)
