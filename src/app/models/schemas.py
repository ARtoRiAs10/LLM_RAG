from pydantic import BaseModel
from datetime import datetime
from .models import DocumentStatus

class DocumentMetadata(BaseModel):
    id: int
    filename: str
    status: DocumentStatus
    created_at: datetime

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    source_documents: list[dict]