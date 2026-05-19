import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from processing.domain.entities import Document
from processing.infrastructure.adapters.parquet_document_reader import (
    ParquetDocumentRepository,
)


def _assert_metadata(documents: list[Document], index: int) -> dict[str, Any]:
    metadata = documents[index].metadata
    assert metadata is not None
    return metadata


@patch("processing.infrastructure.adapters.parquet_document_reader.pd.read_parquet")
def test_load_abstracts_documents_with_metadata(mock_read_parquet: MagicMock) -> None:
    mock_read_parquet.return_value = pd.DataFrame(
        [
            {
                "thesis_id": 1,
                "repo_owner": "owner-a",
                "repo_name": "repo-a",
                "source_path": "docs/memoria.tex",
                "content": "  Abstract text A  ",
                "retrieved_at": "2026-03-01T18:00:00+00:00",
            },
            {
                "thesis_id": 2,
                "repo_owner": "owner-b",
                "repo_name": "repo-b",
                "source_path": "docs/memoria.tex",
                "content": "",
                "retrieved_at": "2026-03-01T18:00:00+00:00",
            },
        ]
    )
    repo = ParquetDocumentRepository(ingestion_data_dir=str(Path("/tmp/ingestion")))

    documents = repo.load_documents(doc_name="abstracts.parquet")

    assert len(documents) == 1
    assert documents[0].text == "Abstract text A"
    metadata = _assert_metadata(documents, 0)
    assert metadata["dataset"] == "abstracts"
    assert metadata["repo_owner"] == "owner-a"
    assert metadata["repo_name"] == "repo-a"
    assert metadata["path"] == "docs/memoria.tex"
    assert metadata["source_url"] == "https://github.com/owner-a/repo-a"


@patch("processing.infrastructure.adapters.parquet_document_reader.pd.read_parquet")
def test_load_readmes(mock_read_parquet: MagicMock) -> None:
    encoded_content = base64.b64encode(b"Readme content").decode("utf-8")
    mock_read_parquet.return_value = pd.DataFrame(
        [
            {
                "thesis_id": 1,
                "content": encoded_content,
                "download_url": "http://url",
            },
            {
                "thesis_id": 2,
                "content": "not_base64_encoded\xff",  # will fail decode
                "download_url": "http://url2",
            },
            {
                "thesis_id": 3,
                "content": None,
                "download_url": "http://url3",
            },
        ]
    )
    repo = ParquetDocumentRepository(ingestion_data_dir=str(Path("/tmp/ingestion")))
    documents = repo.load_documents(doc_name="readmes.parquet")
    assert len(documents) == 1
    assert documents[0].text == "Readme content"
    metadata = _assert_metadata(documents, 0)
    assert metadata["dataset"] == "readmes"
    assert metadata["source_url"] == "http://url"


@patch("processing.infrastructure.adapters.parquet_document_reader.pd.read_parquet")
def test_load_issues(mock_read_parquet: MagicMock) -> None:
    mock_read_parquet.return_value = pd.DataFrame(
        [
            {
                "thesis_id": 1,
                "title": "Bug fix",
                "description": "Fixing the bug",
                "issue_id": 100,
                "repo_owner": "owner",
                "repo_name": "repo",
            },
            {
                "thesis_id": 2,
                "title": None,
                "description": None,
            },
        ]
    )
    repo = ParquetDocumentRepository(ingestion_data_dir=str(Path("/tmp/ingestion")))
    documents = repo.load_documents(doc_name="issues.parquet")
    assert len(documents) == 1
    assert documents[0].text == "Bug fix Fixing the bug"
    metadata = _assert_metadata(documents, 0)
    assert metadata["dataset"] == "issues"
    assert metadata["issue_id"] == 100
    assert metadata["source_url"] == "https://github.com/owner/repo"


@patch("processing.infrastructure.adapters.parquet_document_reader.pd.read_parquet")
def test_load_thesis(mock_read_parquet: MagicMock) -> None:
    texts_data = json.dumps(
        [
            {"contents": "Thesis section 1", "section": "intro", "path": "intro.txt"},
            {"contents": None, "section": "bad", "path": "bad.txt"},
        ]
    )
    mock_read_parquet.return_value = pd.DataFrame(
        [
            {
                "thesis_id": 1,
                "texts": texts_data,
            },
            {
                "thesis_id": 2,
                "texts": "invalid json",
            },
            {
                "thesis_id": 3,
                "texts": None,
            },
        ]
    )
    repo = ParquetDocumentRepository(ingestion_data_dir=str(Path("/tmp/ingestion")))
    documents = repo.load_documents(doc_name="thesis.parquet")
    assert len(documents) == 1
    assert documents[0].text == "Thesis section 1"
    metadata = _assert_metadata(documents, 0)
    assert metadata["dataset"] == "thesis"
    assert metadata["section"] == "intro"
    assert metadata["path"] == "intro.txt"


@patch("processing.infrastructure.adapters.parquet_document_reader.pd.read_parquet")
def test_load_unknown(mock_read_parquet: MagicMock) -> None:
    mock_read_parquet.return_value = pd.DataFrame([{"thesis_id": 1}])
    repo = ParquetDocumentRepository(ingestion_data_dir=str(Path("/tmp/ingestion")))
    documents = repo.load_documents(doc_name="unknown.parquet")
    assert len(documents) == 0


def test_normalize_value() -> None:
    repo = ParquetDocumentRepository(ingestion_data_dir="")

    # Timestamp
    ts = pd.Timestamp("2023-01-01 12:00:00")
    assert repo._normalize_value(ts) == ts.isoformat()

    # Datetime
    dt = datetime(2023, 1, 1, 12, 0, 0)
    assert repo._normalize_value(dt) == dt.isoformat()

    # Primitive types
    assert repo._normalize_value("str") == "str"
    assert repo._normalize_value(1) == 1
    assert repo._normalize_value(None) is None

    # Dict and list
    assert repo._normalize_value({"a": 1}) == '{"a": 1}'
    assert repo._normalize_value([1, 2]) == "[1, 2]"

    # item() fallback
    class ItemMock:
        def item(self) -> int:
            return 42

    assert repo._normalize_value(ItemMock()) == 42

    # Numpy array fallback (item() fails for multi-element array)
    arr = np.array([1, 2])
    assert repo._normalize_value(arr) == str(arr)


def test_ensure_list_of_dicts() -> None:
    repo = ParquetDocumentRepository(ingestion_data_dir="")

    # Valid list
    assert repo._ensure_list_of_dicts([{"a": 1}]) == [{"a": 1}]
    assert repo._ensure_list_of_dicts(["string", {"a": 1}]) == [{"a": 1}]

    # Numpy array representing list of dicts
    arr = np.array([{"a": 1}])
    assert repo._ensure_list_of_dicts(arr) == [{"a": 1}]

    # Numpy array representing other
    arr2 = np.array([1, 2])
    assert repo._ensure_list_of_dicts(arr2) == []

    # Invalid
    assert repo._ensure_list_of_dicts(None) == []
    assert repo._ensure_list_of_dicts("string") == []
