"""PDF document loading utilities for the knowledge base."""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BACKEND_DIR / "docs"
# The current repository stores its sample PDFs here.  Prefer DOCS_DIR whenever
# it exists so deployments can follow the documented backend/docs convention.
LEGACY_DOCS_DIR = BACKEND_DIR.parent / "docs"


def get_docs_directory() -> Path:
    """Return the configured document directory, creating no directories."""
    if DOCS_DIR.exists():
        return DOCS_DIR
    if LEGACY_DOCS_DIR.exists():
        logger.warning("backend/docs does not exist; using %s", LEGACY_DOCS_DIR)
        return LEGACY_DOCS_DIR
    return DOCS_DIR


def load_documents() -> list[Document]:
    """Load every PDF in the document directory as LangChain documents."""
    docs_directory = get_docs_directory()
    if not docs_directory.exists():
        raise FileNotFoundError(f"Document directory does not exist: {docs_directory}")

    documents: list[Document] = []
    pdf_paths = sorted(
        path for path in docs_directory.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"
    )
    for pdf_path in pdf_paths:
        try:
            documents.extend(PyPDFLoader(str(pdf_path)).load())
        except Exception as exc:
            logger.exception("Unable to load PDF: %s", pdf_path)
            raise RuntimeError(f"Unable to load PDF '{pdf_path.name}'") from exc

    logger.info("Loaded %d PDF(s) into %d document page(s).", len(pdf_paths), len(documents))
    return documents


def load_single_document(filepath: str | Path) -> list[Document]:
    """Load one PDF, retained for existing knowledge-base upload workflows."""
    pdf_path = Path(filepath)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file does not exist: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Only PDF files are supported: {pdf_path}")

    try:
        return PyPDFLoader(str(pdf_path)).load()
    except Exception as exc:
        logger.exception("Unable to load PDF: %s", pdf_path)
        raise RuntimeError(f"Unable to load PDF '{pdf_path.name}'") from exc
