"""Vector store service using ChromaDB."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for vector similarity search using ChromaDB."""

    def __init__(self, persist_directory: str, collection_name: str):
        """Initialize vector store."""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )

        self.collection_name = collection_name
        self.collection = None

        logger.info(f"Vector store initialized at {persist_directory}")

    def create_collection(self) -> chromadb.Collection:
        """Create or get collection."""
        try:
            # Delete existing collection if it exists (for fresh start)
            try:
                self.client.delete_collection(name=self.collection_name)
                logger.info(f"Deleted existing collection: {self.collection_name}")
            except:
                pass

            # Create new collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},  # Cosine similarity
            )

            logger.info(f"Created collection: {self.collection_name}")
            return self.collection

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def get_collection(self) -> chromadb.Collection:
        """Get existing collection."""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Retrieved collection: {self.collection_name}")
            return self.collection
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            # Try to create if doesn't exist
            return self.create_collection()

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ):
        """Add documents to collection."""
        if self.collection is None:
            self.get_collection()

        try:
            self.collection.add(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)

            logger.info(f"Added {len(documents)} documents to collection")

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(
        self, query_embedding: List[float], n_results: int = 10, where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents."""
        if self.collection is None:
            self.get_collection()

        try:
            results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results, where=where)

            logger.debug(f"Found {len(results['ids'][0])} results")
            return results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {"ids": [[]], "distances": [[]], "metadatas": [[]], "documents": [[]]}

    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        if self.collection is None:
            self.get_collection()

        try:
            result = self.collection.get(ids=[id])

            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "metadata": result["metadatas"][0],
                    "document": result["documents"][0],
                }
            return None

        except Exception as e:
            logger.error(f"Error getting document by ID: {e}")
            return None

    def count(self) -> int:
        """Get count of documents in collection."""
        if self.collection is None:
            self.get_collection()

        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0

    def delete_collection(self):
        """Delete the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
