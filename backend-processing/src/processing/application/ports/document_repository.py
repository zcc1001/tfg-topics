from abc import ABC, abstractmethod

from processing.domain.entities import Document


class DocumentRepository(ABC):
    @abstractmethod
    def load_documents(self, doc_name: str) -> list[Document]:
        """Loads the list of documents from the repository .

        Raises:
            NotImplementedError: not implemented error

        Returns:
            list[Document]: list of documents
        """
        raise NotImplementedError
