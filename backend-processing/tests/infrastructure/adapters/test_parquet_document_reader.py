from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from processing.infrastructure.adapters.parquet_document_reader import (
    ParquetDocumentRepository,
)


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
    assert documents[0].metadata is not None
    assert documents[0].metadata["dataset"] == "abstracts"
    assert documents[0].metadata["repo_owner"] == "owner-a"
    assert documents[0].metadata["repo_name"] == "repo-a"
    assert documents[0].metadata["path"] == "docs/memoria.tex"
    assert documents[0].metadata["source_url"] == "https://github.com/owner-a/repo-a"
