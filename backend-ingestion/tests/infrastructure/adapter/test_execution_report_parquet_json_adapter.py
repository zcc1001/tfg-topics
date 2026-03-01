import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ingestion.domain.entities.execution_report import ExecutionReport
from ingestion.domain.entities.ingestion_summary import IngestionSummary
from ingestion.infrastructure.adapter.execution_report_parquet_json_adapter import (
    ExecutionReportParquetJsonAdapter,
)


def _make_summary(dataset: str) -> IngestionSummary:
    return IngestionSummary(
        data_type=dataset,
        repos_with_data=["o1/r1"],
        repos_without_data=["o2/r2"],
        with_data_count=1,
        without_data_count=1,
        repo_record_counts={"o1/r1": 3},
    )


def test_save_execution_report_persists_manifest_and_history(tmp_path: Path) -> None:
    adapter = ExecutionReportParquetJsonAdapter(base_dir=str(tmp_path))
    finished_at = datetime.now(timezone.utc)
    report = ExecutionReport(
        run_id="run-001",
        started_at=finished_at,
        finished_at=finished_at,
        status="success",
        selected_targets=["all"],
        dataset_summaries=[_make_summary("issues"), _make_summary("readmes")],
    )

    adapter.save_execution_report(report)

    manifest_path = tmp_path / "executions" / "run-001" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["run_id"] == "run-001"
    assert len(manifest["datasets"]) == 2
    assert manifest["datasets"][0]["data_type"] == "issues"

    history_path = tmp_path / "execution_history.parquet"
    assert history_path.exists()
    history_df = pd.read_parquet(history_path)
    assert len(history_df) == 4
    assert set(history_df["dataset"].tolist()) == {"issues", "readmes"}
    assert set(history_df["has_data"].tolist()) == {True, False}


def test_save_execution_report_appends_history(tmp_path: Path) -> None:
    adapter = ExecutionReportParquetJsonAdapter(base_dir=str(tmp_path))
    now = datetime.now(timezone.utc)
    first = ExecutionReport(
        run_id="run-001",
        started_at=now,
        finished_at=now,
        status="success",
        selected_targets=["issues"],
        dataset_summaries=[_make_summary("issues")],
    )
    second = ExecutionReport(
        run_id="run-002",
        started_at=now,
        finished_at=now,
        status="success",
        selected_targets=["readmes"],
        dataset_summaries=[_make_summary("readmes")],
    )

    adapter.save_execution_report(first)
    adapter.save_execution_report(second)

    history_df = pd.read_parquet(tmp_path / "execution_history.parquet")
    assert len(history_df) == 4
    assert set(history_df["run_id"].tolist()) == {"run-001", "run-002"}
