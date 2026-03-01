import base64
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from processing.application.ports.document_repository import DocumentRepository
from processing.domain.entities import Document

logger = logging.getLogger(__name__)


class ParquetDocumentRepository(DocumentRepository):
    def __init__(self, ingestion_data_dir: str):
        self.ingestion_data_dir = ingestion_data_dir

    def load_documents(self, doc_name: str = "readmes.parquet") -> list[Document]:
        doc_path = os.path.join(self.ingestion_data_dir, doc_name)
        df = pd.read_parquet(doc_path)
        logger.info("Read [%s] documents from Parquet file: [%s]", len(df), doc_path)

        documents: List[Document] = []
        if doc_name == "readmes.parquet":
            documents = self._load_readmes(df)
        elif doc_name == "issues.parquet":
            documents = self._load_issues(df)
        elif doc_name == "thesis.parquet":
            documents = self._load_thesis(df)
        elif doc_name == "abstracts.parquet":
            documents = self._load_abstracts(df)
        else:
            logger.error("Unknown document name: %s", doc_name)

        return documents

    def _load_readmes(self, df: pd.DataFrame) -> List[Document]:
        documents: List[Document] = []

        for _, row in df.iterrows():
            content = row.get("content")
            if not isinstance(content, str):
                continue

            decoded = self._decode_base64(content)
            if decoded is None:
                continue

            metadata = self._build_metadata(
                row,
                dataset="readmes",
                source_url=row.get("download_url"),
            )
            documents.append(Document(text=decoded, metadata=metadata))

        return documents

    def _load_issues(self, df: pd.DataFrame) -> List[Document]:
        documents: List[Document] = []

        for _, row in df.iterrows():
            title = row.get("title") or ""
            description = row.get("description") or ""
            text = f"{title} {description}".strip()
            if not text:
                continue

            metadata = self._build_metadata(
                row,
                dataset="issues",
                source_url=self._build_source_url(row),
            )
            documents.append(Document(text=text, metadata=metadata))

        return documents

    def _load_abstracts(self, df: pd.DataFrame) -> List[Document]:
        documents: List[Document] = []

        for _, row in df.iterrows():
            content = row.get("content")
            if not isinstance(content, str) or not content.strip():
                continue

            source_url = self._build_source_url(row)
            source_path = row.get("source_path")
            path = source_path if isinstance(source_path, str) else None
            metadata = self._build_metadata(
                row,
                dataset="abstracts",
                source_url=source_url,
                path=path,
            )
            documents.append(Document(text=content.strip(), metadata=metadata))

        return documents

    def _load_thesis(self, df: pd.DataFrame) -> List[Document]:
        documents: List[Document] = []

        for _, row in df.iterrows():
            texts_data = row.get("texts")
            items = self._parse_texts(texts_data)
            if not items:
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue
                contents = item.get("contents")
                if not isinstance(contents, str):
                    continue

                section = item.get("section") or "unknown_section"
                path = item.get("path")

                metadata = self._build_metadata(
                    row,
                    dataset="thesis",
                    section=section,
                    path=path,
                )
                documents.append(Document(text=contents, metadata=metadata))

        return documents

    def _build_source_url(self, row: pd.Series) -> Optional[str]:
        repo_owner = row.get("repo_owner")
        repo_name = row.get("repo_name")
        if isinstance(repo_owner, str) and isinstance(repo_name, str):
            return f"https://github.com/{repo_owner}/{repo_name}"
        return None

    def _decode_base64(self, value: str) -> Optional[str]:
        try:
            return base64.b64decode(value).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            logger.warning("Skipping document due to decode error: %s", exc)
            return None

    def _parse_texts(self, texts_data: Any) -> List[Dict[str, Any]]:
        if texts_data is None:
            return []
        if isinstance(texts_data, str):
            try:
                parsed = json.loads(texts_data)
            except json.JSONDecodeError as exc:
                logger.warning("Invalid texts JSON: %s", exc)
                return []
            return self._ensure_list_of_dicts(parsed)
        return self._ensure_list_of_dicts(texts_data)

    def _ensure_list_of_dicts(self, value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if hasattr(value, "tolist"):
            try:
                list_value = value.tolist()
                if isinstance(list_value, list):
                    return [item for item in list_value if isinstance(item, dict)]
            except Exception:  # noqa: BLE001 - defensive conversion
                return []
        return []

    def _build_metadata(
        self,
        row: pd.Series,
        dataset: str,
        source_url: Optional[str] = None,
        section: Optional[str] = None,
        path: Optional[str] = None,
    ) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            "dataset": dataset,
            "thesis_id": self._normalize_value(row.get("thesis_id")),
            "retrieved_at": self._normalize_value(row.get("retrieved_at")),
        }

        if source_url is not None:
            metadata["source_url"] = source_url

        if section is not None:
            metadata["section"] = section

        if path is not None:
            metadata["path"] = path

        issue_id = row.get("issue_id")
        if issue_id is not None:
            metadata["issue_id"] = self._normalize_value(issue_id)

        repo_owner = row.get("repo_owner")
        if repo_owner is not None:
            metadata["repo_owner"] = self._normalize_value(repo_owner)

        repo_name = row.get("repo_name")
        if repo_name is not None:
            metadata["repo_name"] = self._normalize_value(repo_name)

        return metadata

    def _normalize_value(self, value: Any) -> Any:
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=True)
        if isinstance(value, list):
            return json.dumps(value, ensure_ascii=True)
        if hasattr(value, "item"):
            try:
                return value.item()
            except Exception:  # noqa: BLE001 - defensive conversion
                return str(value)
        return str(value)
