from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.core.vector_stores import (
    VectorStoreQuery,
    VectorStoreQueryResult,
)
from typing import List, Any
from llama_index.core.schema import BaseNode


class MockVectorStore(BasePydanticVectorStore):
    """Simple custom Vector Store.

    Stores documents in a simple in-memory dict.

    """

    stores_text: bool = True

    @property
    def client(self) -> None:
        """Get client."""
        return None

    def get(self, text_id: str) -> List[float]:
        """Get embedding."""
        pass

    def add(
        self,
        nodes: List[BaseNode],
    ) -> List[str]:
        """Add nodes to index."""
        pass

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.

        Args:
            ref_doc_id (str): The doc_id of the document to delete.

        """
        pass

    def query(
        self,
        query: VectorStoreQuery,
        **kwargs: Any,
    ) -> VectorStoreQueryResult:
        """Get nodes for response."""
        pass

    def persist(self, persist_path, fs=None) -> None:
        """Persist the SimpleVectorStore to a directory.

        NOTE: we are not implementing this for now.

        """
        pass
