"""Manual smoke test for the RAG module."""

import logging

from rag.document_loader import load_documents
from rag.retriever import retrieve_context
from rag.vector_store import build_vector_db


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    documents = load_documents()
    print(f"Loaded {len(documents)} document page(s).")
    build_vector_db()

    query = "What is the leave policy?"
    print(f"\nQuestion: {query}\n")
    print("Retrieved context:")
    print(retrieve_context(query))


if __name__ == "__main__":
    main()
