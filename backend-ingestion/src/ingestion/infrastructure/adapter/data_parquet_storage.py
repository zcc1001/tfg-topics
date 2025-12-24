import logging
import os
from typing import List, Literal

import pandas as pd

from ingestion.application.ports.storage_port import StoragePort
from ingestion.domain.entities.entities import IssueData, ReadmeData

logger = logging.getLogger(__name__)


class IngestionParquetStorage(StoragePort):
    def __init__(
        self,
        base_dir: str = "data",
        issues_filename: str = "issues.parquet",
        readmes_filename: str = "readmes.parquet",
        buffer_size: int = 500,
        compression: Literal["snappy", "gzip", "brotli", "lz4", "zstd"] = "snappy",
    ):
        os.makedirs(base_dir, exist_ok=True)
        self.base_dir = base_dir
        self.issues_path = os.path.join(base_dir, issues_filename)
        self.readmes_path = os.path.join(base_dir, readmes_filename)
        self.buffer_size = int(buffer_size)
        self.compression: Literal["snappy", "gzip", "brotli", "lz4", "zstd"] = (
            compression
        )
        self._issues_buf: List[IssueData] = []
        self._readmes_buf: List[ReadmeData] = []

    def save_issue(self, issue_data: List[IssueData]) -> None:
        """Save the given issue data to the file .

        Args:
            issue_data (List[IssueData]): list of issue data objects
        """
        if not issue_data:
            logger.warning("No issue data provided to save. Aborting.")
            return

        logger.info(
            "Attempting to save %s issues to %s", len(issue_data), self.issues_path
        )
        is_first_batch = True
        for i in range(0, len(issue_data), self.buffer_size):
            batch = issue_data[i : i + self.buffer_size]
            df = pd.DataFrame([vars(issue) for issue in batch])

            if is_first_batch:
                logger.info(
                    "Writing first batch of %s issues, overwriting %s.",
                    len(batch),
                    self.issues_path,
                )
                df.to_parquet(
                    self.issues_path,
                    engine="fastparquet",
                    compression=self.compression,
                    index=False,
                )
                is_first_batch = False
            else:
                logger.info(
                    "Appending batch of %s issues to %s.", len(batch), self.issues_path
                )
                df.to_parquet(
                    self.issues_path,
                    engine="fastparquet",
                    compression=self.compression,
                    append=True,
                    index=False,
                )
        logger.info(
            "Successfully saved %s issues to %s.", len(issue_data), self.issues_path
        )

    def save_readme(self, readme_data: List[ReadmeData]) -> None:
        """Save the readme data to the file .

        Args:
            readme_data (List[ReadmeData]): list of readme data objects
        """
        if not readme_data:
            logger.warning("No readme data provided to save. Aborting.")
            return

        logger.info(
            "Attempting to save %s readmes to %s", len(readme_data), self.readmes_path
        )
        is_first_batch = True
        for i in range(0, len(readme_data), self.buffer_size):
            batch = readme_data[i : i + self.buffer_size]
            df = pd.DataFrame([vars(readme) for readme in batch])

            if is_first_batch:
                logger.info(
                    "Writing first batch of %s readmes, overwriting %s",
                    len(batch),
                    self.readmes_path,
                )
                df.to_parquet(
                    self.readmes_path,
                    engine="fastparquet",
                    compression=self.compression,
                    index=False,
                )
                is_first_batch = False
            else:
                logger.info(
                    "Appending batch of %s readmes to %s", len(batch), self.readmes_path
                )
                df.to_parquet(
                    self.readmes_path,
                    engine="fastparquet",
                    compression=self.compression,
                    append=True,
                    index=False,
                )
        logger.info(
            "Successfully saved %s readmes to %s", len(readme_data), self.readmes_path
        )
