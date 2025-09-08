"""Database package."""

from .enhanced_vector_store import EnhancedVectorStore, InMemoryVectorStore

# Create a global instance for backward compatibility
try:
    vector_store = EnhancedVectorStore()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to create EnhancedVectorStore, using InMemoryVectorStore: {e}")
    vector_store = InMemoryVectorStore()

__all__ = [
    "EnhancedVectorStore",
    "InMemoryVectorStore",
    "vector_store"
]
