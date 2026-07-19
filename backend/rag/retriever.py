"""Context retrieval for the RAG pipeline."""

from __future__ import annotations

import logging

from rag.vector_store import build_vector_db

logger = logging.getLogger(__name__)


def retrieve_context(query: str) -> str:
    """Return the three most relevant indexed chunks as formatted context."""
    if not query or not query.strip():
        raise ValueError("A non-empty query is required for retrieval.")

    try:
        results = build_vector_db().similarity_search(query.strip(), k=3)
    except Exception as exc:
        logger.exception("Context retrieval failed.")
        raise RuntimeError("Unable to retrieve relevant document context.") from exc

    if not results:
        return "No relevant context found."

    return "\n\n".join(
        f"[Context {position}]\n{document.page_content.strip()}"
        for position, document in enumerate(results, start=1)
    )
