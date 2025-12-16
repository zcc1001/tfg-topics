import logging
import os
from typing import List

import pandas as pd

from application.ports.storage_port import StoragePort
from domain.entities.entities import ReadmeData, IssueData

logger = logging.getLogger(__name__)


class ParquetStorage(StoragePort):
    def __init__(self, base_dir: str = "data",
                 issues_filename: str = "issues.parquet",
                 readmes_filename: str = "readmes.parquet",
                 buffer_size: int = 500,
                 compression: str = "snappy"):
        os.makedirs(base_dir, exist_ok=True)
        self.base_dir = base_dir
        self.issues_path = os.path.join(base_dir, issues_filename)
        self.readmes_path = os.path.join(base_dir, readmes_filename)
        self.buffer_size = int(buffer_size)
        self.compression = compression
        self._issues_buf: List[IssueData] = []
        self._readmes_buf: List[ReadmeData] = []

    def save_issue(self, issue_data: List[IssueData]) -> None:
        if not issue_data:
            logger.warning("No issue data provided to save. Aborting.")
            return

        logger.info(f"Attempting to save {len(issue_data)} issues to '{self.issues_path}'")
        is_first_batch = True
        for i in range(0, len(issue_data), self.buffer_size):
            batch = issue_data[i:i + self.buffer_size]
            df = pd.DataFrame([vars(issue) for issue in batch])

            if is_first_batch:
                logger.info(f"Writing first batch of {len(batch)} issues, overwriting '{self.issues_path}'.")
                df.to_parquet(self.issues_path, engine='fastparquet', compression=self.compression, index=False)
                is_first_batch = False
            else:
                logger.info(f"Appending batch of {len(batch)} issues to '{self.issues_path}'.")
                df.to_parquet(self.issues_path, engine='fastparquet', compression=self.compression, append=True,
                              index=False)
        logger.info(f"Successfully saved {len(issue_data)} issues to '{self.issues_path}'.")

    def save_readme(self, readme_data: List[ReadmeData]) -> None:
        if not readme_data:
            logger.warning("No readme data provided to save. Aborting.")
            return

        logger.info(f"Attempting to save {len(readme_data)} readmes to '{self.readmes_path}'")
        is_first_batch = True
        for i in range(0, len(readme_data), self.buffer_size):
            batch = readme_data[i:i + self.buffer_size]
            df = pd.DataFrame([vars(readme) for readme in batch])

            if is_first_batch:
                logger.info(f"Writing first batch of {len(batch)} readmes, overwriting '{self.readmes_path}'.")
                df.to_parquet(self.readmes_path, engine='fastparquet', compression=self.compression, index=False)
                is_first_batch = False
            else:
                logger.info(f"Appending batch of {len(batch)} readmes to '{self.readmes_path}'.")
                df.to_parquet(self.readmes_path, engine='fastparquet', compression=self.compression, append=True,
                              index=False)
        logger.info(f"Successfully saved {len(readme_data)} readmes to '{self.readmes_path}'.")
