import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

from rag.document_loader import load_documents, load_single_document
from rag.vector_store import append_to_vector_store, build_vector_store

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Knowledge Base"])

DOCS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docs")


def _ensure_docs_dir():
    os.makedirs(DOCS_PATH, exist_ok=True)


# ─── Feature 1 & 2 : Upload + Auto Index ─────────────────────────────────────

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    _ensure_docs_dir()
    save_path = os.path.join(DOCS_PATH, file.filename)

    try:
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)
        logger.info(f"Saved uploaded file: {file.filename}")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    try:
        chunks = load_single_document(save_path)
        append_to_vector_store(chunks)
        logger.info(f"Indexed {file.filename} into vector database.")
    except Exception as e:
        logger.error(f"Failed to index document: {e}")
        raise HTTPException(status_code=500, detail=f"File saved but indexing failed: {str(e)}")

    return {
        "status": "success",
        "message": "Document uploaded successfully",
        "filename": file.filename,
    }


# ─── Feature 3 : List Documents ──────────────────────────────────────────────

@router.get("/documents")
def list_documents():
    _ensure_docs_dir()
    try:
        pdf_files = sorted([f for f in os.listdir(DOCS_PATH) if f.endswith(".pdf")])
        return {"documents": pdf_files}
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Feature 4 : Delete Document ─────────────────────────────────────────────

@router.delete("/documents/{filename}")
def delete_document(filename: str):
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files can be deleted.")

    file_path = os.path.join(DOCS_PATH, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"{filename} not found.")

    try:
        os.remove(file_path)
        logger.info(f"Deleted file: {filename}")
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    try:
        chunks = load_documents()
        if chunks:
            build_vector_store(chunks)
            logger.info("Vector database rebuilt after deletion.")
        else:
            logger.warning("No documents left. Vector database not rebuilt.")
    except Exception as e:
        logger.error(f"Failed to rebuild index after deletion: {e}")
        raise HTTPException(status_code=500, detail=f"File deleted but reindex failed: {str(e)}")

    return {"status": "success", "message": "Document deleted"}


# ─── Feature 5 : Rebuild Vector Database ─────────────────────────────────────

@router.post("/reindex")
def reindex():
    _ensure_docs_dir()
    try:
        chunks = load_documents()
        if not chunks:
            raise HTTPException(status_code=400, detail="No PDF documents found in docs/ folder.")
        build_vector_store(chunks)
        pdf_count = len([f for f in os.listdir(DOCS_PATH) if f.endswith(".pdf")])
        logger.info(f"Reindexed {pdf_count} documents.")
        return {"status": "success", "documents_indexed": pdf_count}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
