import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.models import database, schemas, models
from app.services import document_service
# PyPDFLoader is used here for a quick page count check
from langchain_community.document_loaders import PyPDFLoader

router = APIRouter()

# --- CONSTANTS FOR LIMITS ---
MAX_DOCUMENTS = 20
MAX_PAGES_PER_DOC = 1000

@router.post("/documents", response_model=List[schemas.DocumentMetadata], status_code=status.HTTP_201_CREATED)
def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(database.get_db)
):
    """
    Upload one or more documents (up to 20).
    Each document must not exceed 1000 pages.
    The total number of documents in the system cannot exceed 20.
    """
    # --- VALIDATION 1: Check total number of uploaded files in this request ---
    if len(files) > MAX_DOCUMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot upload more than {MAX_DOCUMENTS} documents in a single request."
        )

    # --- VALIDATION 2: Check total number of documents already in the system ---
    current_doc_count = db.query(models.Document).count()
    if (current_doc_count + len(files)) > MAX_DOCUMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This upload would exceed the system's limit of {MAX_DOCUMENTS} total documents. "
                   f"Currently {current_doc_count} documents exist."
        )

    # --- Process each file ---
    processed_documents_metadata = []
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        file_path = os.path.join(upload_dir, file.filename)

        # Save the file temporarily to check its page count
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # --- VALIDATION 3: Check PDF page count ---
            try:
                loader = PyPDFLoader(file_path)
                pages = loader.load() # This loads the document to get page info
                page_count = len(pages)
                if page_count > MAX_PAGES_PER_DOC:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Document '{file.filename}' exceeds the maximum of {MAX_PAGES_PER_DOC} pages. It has {page_count} pages."
                    )
            except Exception as e:
                # This catches errors if the file is not a valid PDF or is corrupted
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not process document '{file.filename}'. It may not be a valid PDF. Error: {e}"
                )

            # If all validations pass, start the real processing
            # For a real-world app, you'd use a background task runner like Celery here.
            db_document = document_service.process_and_store_document(db, file_path, file.filename)
            
            if db_document.status == models.DocumentStatus.FAILED:
                # We raise a 500 here because the failure is on the server side after validation passed
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to process document '{file.filename}' after validation."
                )
            
            processed_documents_metadata.append(db_document)

        finally:
            # Ensure the temporary file is cleaned up even if an error occurs
            if os.path.exists(file_path):
                os.remove(file_path)

    return processed_documents_metadata


@router.get("/documents/{doc_id}", response_model=schemas.DocumentMetadata)
def get_document_status(
    doc_id: int,
    db: Session = Depends(database.get_db)
):
    """
    Retrieve the metadata and processing status of a specific document.
    """
    db_document = document_service.get_document_metadata(db, doc_id)
    if db_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return db_document


@router.post("/query", response_model=schemas.QueryResponse)
def query_system(
    request: schemas.QueryRequest
):
    """
    Ask a question based on the content of the uploaded documents.
    """
    try:
        # We need to import rag_service here to avoid circular dependencies at startup
        from app.services import rag_service
        result = rag_service.query_rag_pipeline(request.query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the query: {e}"
        )