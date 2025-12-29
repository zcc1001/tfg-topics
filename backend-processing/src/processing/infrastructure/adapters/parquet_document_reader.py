import base64
import json
import logging
import os

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
        logger.info("Read [%s]] documents from Parquet file: [%s]", len(df), doc_path)

        documents = []
        if doc_name == "readmes.parquet":
            documents = [
                Document(
                    text=base64.b64decode(row["content"]).decode("utf-8"),
                    source=row["download_url"],
                )
                for _, row in df.iterrows()
            ]
        elif doc_name == "issues.parquet":
            documents = [
                Document(
                    text=row["title"] + " " + row["description"],
                    source=(
                        f"https://github.com/{row['repo_owner']}/{row['repo_name']}"
                    ),
                )
                for _, row in df.iterrows()
                if (row["title"] + " " + row["description"]).strip()
            ]
        elif doc_name == "thesis.parquet":
            for _, row in df.iterrows():
                texts_data = row["texts"]
                if isinstance(texts_data, str):
                    texts_data = json.loads(texts_data)

                source_url = (
                    f"https://github.com/{row['repo_owner']}/{row['repo_name']}"
                )

                for item in texts_data:
                    if "contents" not in item:
                        continue

                    section_path = item.get("path", "unknown_section")
                    section_name = section_path.replace(".tex", "").split("/")[-1]

                    documents.append(
                        Document(
                            text=item["contents"],
                            source=source_url,
                            metadata={
                                "section": section_name,
                                "path": section_path,
                            },
                        )
                    )
        else:
            logger.error("Unknown document name: %s", {doc_name})

        return documents
