import logging
import re
from typing import Any, List, Optional, Tuple
from urllib.parse import urlparse

import pandas as pd

from ingestion.application.ports.repo_list_reader import RepoListReaderPort
from ingestion.domain.entities.entities import ThesisInfo

logger = logging.getLogger(__name__)


class RepoListCsvReaderPort(RepoListReaderPort):
    """Creates a reader for the repository list ."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def fetch_repo_list(self) -> List[ThesisInfo]:
        df = self._load_csv()

        df = df.reset_index(drop=True)
        df["thesis_id"] = df.index

        repos: List[ThesisInfo] = []

        for row in df.itertuples(index=False):
            repo_url = self._normalize_str(row.repository_url)
            owner_repo = self._extract_owner_repo(repo_url)

            if not owner_repo:
                logger.warning(
                    "Skipping row with invalid or unsupported GitHub repository URL: '%s'",
                    repo_url,
                )
                continue

            owner, repo = owner_repo

            try:
                thesis_id = int(str(row.thesis_id))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid thesis_id value: {row.thesis_id}") from exc

            repos.append(
                ThesisInfo(
                    thesis_id=thesis_id,
                    repo_owner=owner,
                    repo_name=repo,
                    title=self._normalize_str(row.title),
                    tutor=self._normalize_str(row.tutors),
                    student=self._normalize_str(row.students),
                    presentation_date=self._normalize_str(row.presentation_date),
                    assignment_date=self._normalize_str(row.assignment_date),
                    grade=self._normalize_str(row.grade),
                    repository_url=repo_url,
                )
            )

        return repos

    def _load_csv(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.file_path)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Repository list CSV not found: '{self.file_path}'"
            ) from exc
        except pd.errors.ParserError as exc:
            raise ValueError(f"Malformed CSV file: '{self.file_path}'") from exc

    @staticmethod
    def _normalize_str(value: Any) -> str:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        return str(value).strip()

    @staticmethod
    def _extract_owner_repo(url: str) -> Optional[Tuple[str, str]]:
        if not url:
            return None

        url = url.strip().rstrip("/")

        # SSH format: git@github.com:owner/repo.git
        ssh_pattern = (
            r"^(?:git@|ssh://git@)[^/:]+[:/]"
            r"(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$"
        )
        match = re.match(ssh_pattern, url)
        if match:
            return match.group("owner"), match.group("repo")

        # HTTPS format: https://github.com/owner/repo
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            repo = parts[1].removesuffix(".git")
            return parts[0], repo

        return None
