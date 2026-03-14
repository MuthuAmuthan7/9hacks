"""
Retriever service for retrieving medical knowledge from ChromaDB vector database.
"""
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams
import config


class RetrieverService:
    """Service for retrieving documents from vector database."""

    def __init__(self):
        """Initialize the retriever service with embeddings and ChromaDB."""
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": False}
        )

        # # Initialize Qdrant client
        # self.client = QdrantClient(
        #     host=config.QDRANT_HOST,
        #     port=config.QDRANT_PORT,
        #     timeout=60
        # )

        self.collection_name = config.COLLECTION_NAME
        self.vector_store = None
        self._initialized = False

    def initialize(self):
        """Initialize the vector store connection."""
        if self._initialized:
            return

        try:
            # # Old Qdrant initialization
            # collections = self.client.get_collections()
            # collection_names = [col.name for col in collections.collections]
            #
            # if self.collection_name not in collection_names:
            #     vector_size = len(self.embedding_model.embed_query("test"))
            #     self.client.create_collection(
            #         collection_name=self.collection_name,
            #         vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            #     )
            #
            # self.vector_store = QdrantVectorStore.from_existing_collection(
            #     client=self.client,
            #     collection_name=self.collection_name,
            #     embedding=self.embedding_model
            # )

            # Initialize local ChromaDB vector store
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
                persist_directory=config.CHROMA_PERSIST_DIR
            )
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize vector store: {str(e)}")

    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of Document objects to add

        Returns:
            List of document IDs
        """
        if not self._initialized:
            self.initialize()

        try:
            doc_ids = self.vector_store.add_documents(documents)
            return doc_ids
        except Exception as e:
            raise RuntimeError(f"Failed to add documents: {str(e)}")

    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for documents similar to the query.

        Args:
            query: Search query string
            k: Number of results to return

        Returns:
            List of Document objects matching the query
        """
        if not self._initialized:
            self.initialize()

        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to search documents: {str(e)}")

    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """
        Search for documents with similarity scores.

        Args:
            query: Search query string
            k: Number of results to return

        Returns:
            List of (Document, score) tuples
        """
        if not self._initialized:
            self.initialize()

        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to search documents with scores: {str(e)}")

    def clear_collection(self):
        """Clear all documents from the collection."""
        if not self._initialized:
            self.initialize()

        try:
            # # Old Qdrant clear
            # self.client.delete_collection(self.collection_name)

            # ChromaDB: delete and reinitialize the collection
            self.vector_store.delete_collection()
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
                persist_directory=config.CHROMA_PERSIST_DIR
            )
            self._initialized = False
        except Exception as e:
            raise RuntimeError(f"Failed to clear collection: {str(e)}")


# Global retriever instance
_retriever_service: Optional[RetrieverService] = None


def get_retriever_service() -> RetrieverService:
    """Get or create the global retriever service instance."""
    global _retriever_service
    if _retriever_service is None:
        _retriever_service = RetrieverService()
    return _retriever_service
