from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from ingestion.domain.entities.entities import IssueData
from ingestion.infrastructure.adapter.ingestion_parquet_storage import (
    IngestionParquetStorage,
)


def test_save_issue_calls_to_parquet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ensure save_issue invokes pandas to_parquet once for non-empty input."""
    calls: list = []

    def stub_to_parquet(
        _self: pd.DataFrame, path: str, *_: list, **kwargs: dict
    ) -> None:
        calls.append((path, kwargs))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("parquet-mock", encoding="utf-8")

    monkeypatch.setattr(pd.DataFrame, "to_parquet", stub_to_parquet)

    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    issues = [
        IssueData(
            thesis_id=1,
            repo_owner="owner",
            repo_name="repo",
            issue_id=1,
            title="t1",
            description="d1",
            retrieved_at=datetime.now(timezone.utc),
        ),
        IssueData(
            thesis_id=2,
            repo_owner="owner",
            repo_name="repo",
            issue_id=2,
            title="t2",
            description="d2",
            retrieved_at=datetime.now(timezone.utc),
        ),
        IssueData(
            thesis_id=3,
            repo_owner="owner",
            repo_name="repo",
            issue_id=3,
            title="t3",
            description="d3",
            retrieved_at=datetime.now(timezone.utc),
        ),
    ]
    storage.save_issue(issues)

    assert len(calls) == 1
    assert not calls[0][1].get("append")

    assert Path(storage.issues_path).exists()


def test_save_readme_empty_no_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No file is written when save_readme receives an empty list."""
    calls: list = []

    def stub_to_parquet(_self: pd.DataFrame, path: str, *_: list, **__: dict) -> None:
        calls.append(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("parquet-mock", encoding="utf-8")

    monkeypatch.setattr(pd.DataFrame, "to_parquet", stub_to_parquet)

    storage = IngestionParquetStorage(base_dir=str(tmp_path))
    storage.save_readme([])

    assert not calls
