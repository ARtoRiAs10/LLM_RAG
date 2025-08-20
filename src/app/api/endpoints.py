import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.models import database, schemas, models
from app.services import document_service, rag_service

router = APIRouter()

@router.post("/documents", response_model=schemas.DocumentMetadata, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_document = document_service.process_and_store_document(db, file_path, file.filename)
    
    if db_document.status == models.DocumentStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document."
        )
    return db_document

@router.get("/documents/{doc_id}", response_model=schemas.DocumentMetadata)
def get_document_status(
    doc_id: int,
    db: Session = Depends(database.get_db)
):
    db_document = document_service.get_document_metadata(db, doc_id)
    if db_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return db_document

@router.post("/query", response_model=schemas.QueryResponse)
def query_system(
    request: schemas.QueryRequest
):
    try:
        result = rag_service.query_rag_pipeline(request.query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the query: {e}"
        )