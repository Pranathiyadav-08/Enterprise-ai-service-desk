"""FAISS vector-store lifecycle management for RAG."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.document_loader import load_documents

logger = logging.getLogger(__name__)

VECTOR_DB_PATH = Path(__file__).resolve().parent.parent / "vector_db"
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_embeddings() -> OllamaEmbeddings:
    """Create the embedding client used by the FAISS index."""
    return OllamaEmbeddings(model=EMBEDDING_MODEL)


def _index_exists() -> bool:
    return (VECTOR_DB_PATH / "index.faiss").is_file() and (VECTOR_DB_PATH / "index.pkl").is_file()


def _split_documents(documents: Sequence[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(list(documents))


def _create_vector_db(documents: Sequence[Document]) -> FAISS:
    chunks = _split_documents(documents)
    if not chunks:
        raise ValueError("No document content is available to build the vector database.")

    try:
        vector_db = FAISS.from_documents(chunks, get_embeddings())
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        vector_db.save_local(str(VECTOR_DB_PATH))
    except Exception as exc:
        logger.exception("Failed to build vector database.")
        raise RuntimeError("Failed to build the FAISS vector database.") from exc

    logger.info("Built FAISS vector database with %d chunks at %s", len(chunks), VECTOR_DB_PATH)
    return vector_db


def build_vector_db() -> FAISS:
    """Load an existing index, or build one from all PDFs when none exists."""
    if _index_exists():
        logger.info("Loading existing FAISS vector database from %s", VECTOR_DB_PATH)
        return load_vector_db()
    return _create_vector_db(load_documents())


def load_vector_db() -> FAISS:
    """Load the persisted FAISS vector database."""
    if not _index_exists():
        raise FileNotFoundError(f"FAISS vector database does not exist at {VECTOR_DB_PATH}")
    try:
        return FAISS.load_local(
            str(VECTOR_DB_PATH), get_embeddings(), allow_dangerous_deserialization=True
        )
    except Exception as exc:
        logger.exception("Failed to load vector database from %s", VECTOR_DB_PATH)
        raise RuntimeError("Failed to load the FAISS vector database.") from exc


def rebuild_vector_db() -> FAISS:
    """Recreate the FAISS index from all current PDF documents."""
    logger.info("Rebuilding FAISS vector database.")
    return _create_vector_db(load_documents())


# Compatibility helpers used by the existing upload router. They keep chunking
# centralized here while the public RAG lifecycle API above remains canonical.
def build_vector_store(documents: Sequence[Document]) -> FAISS:
    return _create_vector_db(documents)


def append_to_vector_store(documents: Sequence[Document]) -> FAISS:
    chunks = _split_documents(documents)
    if not chunks:
        raise ValueError("No document content is available to add to the vector database.")
    try:
        vector_db = load_vector_db() if _index_exists() else FAISS.from_documents(chunks, get_embeddings())
        if _index_exists():
            vector_db.add_documents(chunks)
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        vector_db.save_local(str(VECTOR_DB_PATH))
        return vector_db
    except Exception as exc:
        logger.exception("Failed to update vector database.")
        raise RuntimeError("Failed to update the FAISS vector database.") from exc


def get_or_create_vector_store(documents: Sequence[Document] | None = None) -> FAISS:
    if _index_exists():
        return load_vector_db()
    return _create_vector_db(documents) if documents is not None else build_vector_db()
