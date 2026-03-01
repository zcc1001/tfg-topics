import json
import logging
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any

import pandas as pd

from ingestion.application.ports.execution_report_port import ExecutionReportPort
from ingestion.domain.entities.execution_report import ExecutionReport
from ingestion.domain.entities.ingestion_summary import IngestionSummary

logger = logging.getLogger(__name__)


class ExecutionReportParquetJsonAdapter(ExecutionReportPort):
    def __init__(
        self,
        base_dir: str = "data",
        executions_dirname: str = "executions",
        history_filename: str = "execution_history.parquet",
        engine: str = "pyarrow",
        compression: str = "snappy",
    ) -> None:
        self.base_dir = base_dir
        self.executions_dir = os.path.join(base_dir, executions_dirname)
        self.history_path = os.path.join(base_dir, history_filename)
        self.engine = engine
        self.compression = compression
        os.makedirs(self.executions_dir, exist_ok=True)

    def save_execution_report(self, report: ExecutionReport) -> None:
        self._save_manifest_json(report)
        self._append_history_rows(report)

    def _save_manifest_json(self, report: ExecutionReport) -> None:
        run_dir = os.path.join(self.executions_dir, report.run_id)
        os.makedirs(run_dir, exist_ok=True)
        target_path = os.path.join(run_dir, "manifest.json")

        payload = {
            "run_id": report.run_id,
            "started_at": report.started_at.isoformat(),
            "finished_at": report.finished_at.isoformat(),
            "status": report.status,
            "selected_targets": report.selected_targets,
            "error_message": report.error_message,
            "datasets": [
                self._summary_to_dict(summary) for summary in report.dataset_summaries
            ],
        }

        with open(target_path, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=True, indent=2)

        logger.info("Execution manifest saved to %s", target_path)

    def _append_history_rows(self, report: ExecutionReport) -> None:
        rows: list[dict[str, Any]] = []
        for summary in report.dataset_summaries:
            rows.extend(
                self._summary_rows(
                    run_id=report.run_id,
                    status=report.status,
                    finished_at=report.finished_at,
                    summary=summary,
                )
            )

        if not rows:
            logger.info("No dataset rows to persist for run_id=%s", report.run_id)
            return

        new_df = pd.DataFrame(rows)
        if os.path.exists(self.history_path):
            existing_df = pd.read_parquet(self.history_path, engine=self.engine)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df

        combined_df.to_parquet(
            self.history_path,
            engine=self.engine,
            compression=self.compression,
            index=False,
        )
        logger.info(
            "Execution history persisted to %s with %s new rows",
            self.history_path,
            len(new_df),
        )

    @staticmethod
    def _summary_rows(
        run_id: str,
        status: str,
        finished_at: datetime,
        summary: IngestionSummary,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for repo in summary.repos_with_data:
            owner, repo_name = ExecutionReportParquetJsonAdapter._split_repo_full_name(
                repo
            )
            rows.append(
                {
                    "run_id": run_id,
                    "dataset": summary.data_type,
                    "repo_owner": owner,
                    "repo_name": repo_name,
                    "has_data": True,
                    "records_count": summary.repo_record_counts.get(repo, 0),
                    "executed_at": finished_at,
                    "status": status,
                    "error_message": None,
                }
            )
        for repo in summary.repos_without_data:
            owner, repo_name = ExecutionReportParquetJsonAdapter._split_repo_full_name(
                repo
            )
            rows.append(
                {
                    "run_id": run_id,
                    "dataset": summary.data_type,
                    "repo_owner": owner,
                    "repo_name": repo_name,
                    "has_data": False,
                    "records_count": 0,
                    "executed_at": finished_at,
                    "status": status,
                    "error_message": None,
                }
            )
        return rows

    @staticmethod
    def _split_repo_full_name(repo_full_name: str) -> tuple[str, str]:
        parts = repo_full_name.split("/", maxsplit=1)
        if len(parts) != 2:
            return "", repo_full_name
        return parts[0], parts[1]

    @staticmethod
    def _summary_to_dict(summary: IngestionSummary) -> dict[str, Any]:
        summary_dict = asdict(summary)
        summary_dict["repos_with_data"] = sorted(summary.repos_with_data)
        summary_dict["repos_without_data"] = sorted(summary.repos_without_data)
        return summary_dict
