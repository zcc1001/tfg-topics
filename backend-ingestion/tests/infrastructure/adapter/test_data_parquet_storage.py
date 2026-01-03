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
    """Ensure save_issue invokes pandas to_parquet; handle append behavior."""
    calls: list = []

    def stub_to_parquet(
        _self: pd.DataFrame, path: str, *_: list, **kwargs: dict
    ) -> None:
        calls.append((path, kwargs))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("parquet-mock", encoding="utf-8")

    monkeypatch.setattr(pd.DataFrame, "to_parquet", stub_to_parquet)

    storage = IngestionParquetStorage(base_dir=str(tmp_path), buffer_size=2)
    issues = [
        IssueData("owner", "repo", 1, "t1", "d1", datetime.now(timezone.utc)),
        IssueData("owner", "repo", 2, "t2", "d2", datetime.now(timezone.utc)),
        IssueData("owner", "repo", 3, "t3", "d3", datetime.now(timezone.utc)),
    ]
    storage.save_issue(issues)

    assert len(calls) >= 1

    if len(calls) >= 2:
        assert not calls[0][1].get("append")
        assert calls[1][1].get("append") is True

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
