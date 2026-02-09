import logging
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, List, TypeVar, cast

import pandas as pd

from ingestion.application.ports.storage_port import StoragePort
from ingestion.domain.entities.entities import (
    IssueData,
    ReadmeData,
    ThesisData,
    ThesisInfo,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class IngestionParquetStorage(StoragePort):
    """A storage adapter that saves data in Parquet format."""

    def __init__(
        self,
        base_dir: str = "data",
        issues_filename: str = "issues.parquet",
        readmes_filename: str = "readmes.parquet",
        thesis_filename: str = "thesis.parquet",
        thesis_metadata_filename: str = "metadata.parquet",
        engine: str = "pyarrow",
        compression: str = "snappy",
    ):
        os.makedirs(base_dir, exist_ok=True)
        self.base_dir = base_dir
        self.issues_path = os.path.join(base_dir, issues_filename)
        self.readmes_path = os.path.join(base_dir, readmes_filename)
        self.thesis_path = os.path.join(base_dir, thesis_filename)
        self.thesis_metadata_path = os.path.join(base_dir, thesis_metadata_filename)
        self.engine = engine
        self.compression = compression

    def save_issue(self, issue_data: List[IssueData]) -> None:
        self._save_entities(
            data=issue_data,
            path=self.issues_path,
            entity_name="issues",
        )

    def save_readme(self, readme_data: List[ReadmeData]) -> None:
        self._save_entities(
            data=readme_data,
            path=self.readmes_path,
            entity_name="readmes",
        )

    def save_thesis_data(self, thesis_data: List[ThesisData]) -> None:
        self._save_entities(
            data=thesis_data,
            path=self.thesis_path,
            entity_name="thesis",
        )

    def save_thesis_metadata(self, theses: List[ThesisInfo]) -> None:
        """
        Persist academic thesis metadata for downstream processing.
        """
        if not theses:
            logger.warning("No thesis metadata provided to save. Skipping.")
            return

        target_path = self.thesis_metadata_path

        logger.info(
            "Saving %s thesis metadata entries to %s",
            len(theses),
            target_path,
        )

        records = []
        for t in theses:
            year = None
            try:
                year = (
                    datetime.strptime(t.presentation_date, "%d/%m/%Y").year
                    if t.presentation_date
                    else None
                )
            except ValueError:
                logger.warning(
                    "Invalid presentation_date '%s' for thesis_id=%s",
                    t.presentation_date,
                    t.thesis_id,
                )

            records.append(
                {
                    "thesis_id": t.thesis_id,
                    "title": t.title,
                    "tutor": t.tutor,
                    "student": t.student,
                    "year": year,
                    "grade": self._safe_float(t.grade),
                    "repository_url": t.repository_url,
                    "repo_owner": t.repo_owner,
                    "repo_name": t.repo_name,
                }
            )

        df = pd.DataFrame(records)

        df.to_parquet(
            target_path,
            engine=self.engine,
            compression=self.compression,
            index=False,
        )

        logger.info(
            "Successfully persisted thesis metadata (%s entries)",
            len(df),
        )

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    # ---------- Internal helpers ----------

    def _save_entities(
        self,
        data: List[T],
        path: str,
        entity_name: str,
    ) -> None:
        if not data:
            logger.warning("No %s data provided to save. Skipping.", entity_name)
            return

        logger.info(
            "Saving %s %s entries to %s",
            len(data),
            entity_name,
            path,
        )

        new_df = pd.DataFrame([asdict(cast(Any, item)) for item in data])

        new_df.to_parquet(
            path,
            engine=self.engine,
            compression=self.compression,
            index=False,
        )

        logger.info(
            "Successfully persisted %s %s entries (total: %s)",
            len(data),
            entity_name,
            len(new_df),
        )

    @staticmethod
    def _validate_schema(
        existing_df: pd.DataFrame,
        new_df: pd.DataFrame,
        entity_name: str,
    ) -> None:
        if set(existing_df.columns) != set(new_df.columns):
            raise ValueError(
                f"Schema mismatch when appending {entity_name} data. "
                f"Existing columns: {list(existing_df.columns)} | "
                f"New columns: {list(new_df.columns)}"
            )
