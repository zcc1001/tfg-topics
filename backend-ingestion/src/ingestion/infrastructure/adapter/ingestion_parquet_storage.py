import logging
import os
from dataclasses import asdict
from typing import List

import pandas as pd

from ingestion.application.ports.storage_port import StoragePort
from ingestion.domain.entities.entities import IssueData, ReadmeData, ThesisData

logger = logging.getLogger(__name__)


class IngestionParquetStorage(StoragePort):
    def __init__(
        self,
        base_dir: str = "data",
        issues_filename: str = "issues.parquet",
        readmes_filename: str = "readmes.parquet",
        thesis_filename: str = "thesis.parquet",
        buffer_size: int = 500,
        compression: str = "snappy",
    ):
        os.makedirs(base_dir, exist_ok=True)
        self.base_dir = base_dir
        self.issues_path = os.path.join(base_dir, issues_filename)
        self.readmes_path = os.path.join(base_dir, readmes_filename)
        self.thesis_path = os.path.join(base_dir, thesis_filename)
        self.buffer_size = int(buffer_size)
        self.compression = compression
        self._issues_buf: List[IssueData] = []
        self._readmes_buf: List[ReadmeData] = []

    def save_issue(self, issue_data: List[IssueData]) -> None:
        if not issue_data:
            logger.warning("No issue data provided to save. Aborting.")
            return

        logger.info(
            "Attempting to save/append %s issues to %s",
            len(issue_data),
            self.issues_path,
        )
        df = pd.DataFrame([asdict(issue) for issue in issue_data])

        if os.path.exists(self.issues_path):
            existing_df = pd.read_parquet(self.issues_path)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_parquet(
            self.issues_path,
            engine="fastparquet",
            compression=self.compression,
            index=False,
        )
        logger.info(
            "Successfully saved/appended %s issues. Total issues in %s: %s.",
            len(issue_data),
            self.issues_path,
            len(df),
        )

    def save_readme(self, readme_data: List[ReadmeData]) -> None:
        if not readme_data:
            logger.warning("No readme data provided to save. Aborting.")
            return

        logger.info(
            "Attempting to save/append %s readmes to %s",
            len(readme_data),
            self.readmes_path,
        )
        df = pd.DataFrame([asdict(readme) for readme in readme_data])

        if os.path.exists(self.readmes_path):
            existing_df = pd.read_parquet(self.readmes_path)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_parquet(
            self.readmes_path,
            engine="fastparquet",
            compression=self.compression,
            index=False,
        )
        logger.info(
            "Successfully saved/appended %s readmes. Total readmes in %s: %s.",
            len(readme_data),
            self.readmes_path,
            len(df),
        )

    def save_thesis_data(self, thesis_data: List[ThesisData]) -> None:
        if not thesis_data:
            logger.warning("No thesis data provided to save. Aborting.")
            return

        logger.info(
            "Attempting to save/append %s thesis data to %s",
            len(thesis_data),
            self.thesis_path,
        )
        df = pd.DataFrame([asdict(thesis) for thesis in thesis_data])

        if os.path.exists(self.thesis_path):
            existing_df = pd.read_parquet(self.thesis_path)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_parquet(
            self.thesis_path,
            engine="fastparquet",
            compression=self.compression,
            index=False,
        )
        logger.info(
            "Successfully saved/appended %s thesis data. Total thesis data in %s: %s.",
            len(thesis_data),
            self.thesis_path,
            len(df),
        )
