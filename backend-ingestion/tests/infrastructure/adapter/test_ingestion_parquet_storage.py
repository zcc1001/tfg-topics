import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pandas as pd
import pytest

from ingestion.domain.entities.entities import (
    AbstractData,
    IssueData,
    ReadmeData,
    TextData,
    ThesisData,
    ThesisInfo,
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
                thesis_id=i,
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

    def _factory(count: int = 1) -> list[ReadmeData]:
        return [
            ReadmeData(
                thesis_id=i,
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
                thesis_id=i,
                texts=[TextData(contents=f"text {i}", section=f"section {i}")],
                retrieved_at=datetime.now(timezone.utc),
            )
            for i in range(count)
        ]

    return _factory


@pytest.fixture
def abstract_data_factory() -> Callable[[int], list[AbstractData]]:
    """Fixture that returns a factory for creating AbstractData objects."""

    def _factory(count: int = 1) -> list[AbstractData]:
        return [
            AbstractData(
                thesis_id=i,
                repo_owner="owner",
                repo_name=f"repo{i}",
                source_path="docs/memoria.tex",
                content=f"abstract {i}",
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
    """A second save_issue call rewrites parquet with the latest payload."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    issues1 = issue_data_factory(1)
    storage.save_issue(issues1)

    df1 = pd.read_parquet(storage.issues_path)
    assert len(df1) == 1

    issues2 = issue_data_factory(2)[1:]  # Create a second, different issue
    storage.save_issue(issues2)

    df2 = pd.read_parquet(storage.issues_path)
    assert len(df2) == 1
    assert df2["issue_id"].tolist() == [1]


def test_save_readme(
    tmp_path: Path, readme_data_factory: Callable[[int], list[ReadmeData]]
) -> None:
    """Save readme entries to parquet and assert they are present."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    readmes = readme_data_factory(2)

    storage.save_readme(readmes)

    df = pd.read_parquet(storage.readmes_path)
    assert len(df) == 2
    assert df["thesis_id"].tolist() == [0, 1]


def test_save_thesis_data(
    tmp_path: Path, thesis_data_factory: Callable[[int], list[ThesisData]]
) -> None:
    """Persist thesis extracted texts and validate structure in parquet."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    thesis_data = thesis_data_factory(2)

    storage.save_thesis_data(thesis_data)

    df = pd.read_parquet(storage.thesis_path)
    assert len(df) == 2
    assert df["thesis_id"].tolist() == [0, 1]

    texts = df["texts"][0]
    if isinstance(texts, str):
        texts = json.loads(texts)
    assert len(texts) == 1


def test_save_abstracts_data(
    tmp_path: Path, abstract_data_factory: Callable[[int], list[AbstractData]]
) -> None:
    """Persist abstract data and validate structure in parquet."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    abstracts_data = abstract_data_factory(2)

    storage.save_abstracts_data(abstracts_data)

    df = pd.read_parquet(storage.abstracts_path)
    assert len(df) == 2
    assert df["thesis_id"].tolist() == [0, 1]
    assert df["source_path"].tolist() == ["docs/memoria.tex", "docs/memoria.tex"]


def test_save_empty_lists(tmp_path: Path) -> None:
    """Saving empty lists should not create output files."""
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    storage.save_issue([])
    storage.save_readme([])
    storage.save_thesis_data([])
    storage.save_abstracts_data([])

    assert not os.path.exists(storage.issues_path)
    assert not os.path.exists(storage.readmes_path)
    assert not os.path.exists(storage.thesis_path)
    assert not os.path.exists(storage.abstracts_path)


def test_save_thesis_metadata(tmp_path: Path) -> None:
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    data = [
        ThesisInfo(
            thesis_id=1,
            title="t",
            tutor="tu",
            student="s",
            presentation_date="15/06/2023",
            assignment_date="",
            grade="9,5",
            repository_url="u",
            repo_owner="o",
            repo_name="r",
        ),
        ThesisInfo(
            thesis_id=2,
            title="t2",
            tutor="tu2",
            student="s2",
            presentation_date="invalid",
            assignment_date="",
            grade="not a float",
            repository_url="u2",
            repo_owner="o2",
            repo_name="r2",
        ),
    ]
    storage.save_thesis_metadata(data)
    assert os.path.exists(storage.thesis_metadata_path)
    df = pd.read_parquet(storage.thesis_metadata_path)
    assert len(df) == 2
    assert df.iloc[0]["year"] == 2023
    assert df.iloc[0]["grade"] == 9.5
    assert pd.isna(df.iloc[1]["year"])
    assert pd.isna(df.iloc[1]["grade"])


def test_save_thesis_metadata_empty(tmp_path: Path) -> None:
    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    storage.save_thesis_metadata([])
    assert not os.path.exists(storage.thesis_metadata_path)


def test_validate_schema_mismatch() -> None:
    df1 = pd.DataFrame({"A": [1]})
    df2 = pd.DataFrame({"B": [2]})
    with pytest.raises(ValueError, match="Schema mismatch"):
        IngestionParquetStorage._validate_schema(df1, df2, "test")


def test_validate_schema_success() -> None:
    df1 = pd.DataFrame({"A": [1]})
    df2 = pd.DataFrame({"A": [2]})
    IngestionParquetStorage._validate_schema(df1, df2, "test")
