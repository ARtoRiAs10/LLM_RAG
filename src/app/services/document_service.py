import os
from sqlalchemy.orm import Session
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models # <-- IMPORT Qdrant models
from app.models import models
from app.core.config import settings

# --- INITIALIZE CORE COMPONENTS ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# --- START OF CORRECTED CONNECTION AND INITIALIZATION LOGIC ---

# 1. Create a native Qdrant client that connects to your cloud instance.
client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

# 2. ADD THIS BLOCK: Explicitly create the collection if it doesn't exist.
#    'recreate_collection' is idempotent - it works even if the collection is already there.
#    We must specify the vector size (384 for all-MiniLM-L6-v2) and distance metric.
client.recreate_collection(
    collection_name="rag_documents",
    vectors_config=rest_models.VectorParams(size=384, distance=rest_models.Distance.COSINE),
)

# 3. Initialize the LangChain Qdrant object with the client.
vectorstore = Qdrant(
    client=client,
    collection_name="rag_documents",
    embeddings=embeddings,
)
# --- END OF CORRECTED LOGIC ---

# --- SERVICE FUNCTIONS (no changes needed) ---
def process_and_store_document(db: Session, file_path: str, filename: str) -> models.Document:
    # ... (rest of the file is unchanged)
    db_document = models.Document(filename=filename, status=models.DocumentStatus.PROCESSING)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split(text_splitter)
        
        for page in pages:
            page.metadata["document_id"] = db_document.id
            page.metadata["filename"] = filename

        vectorstore.add_documents(documents=pages)

        db_document.status = models.DocumentStatus.COMPLETED
        db.commit()
        db.refresh(db_document)
    except Exception as e:
        db_document.status = models.DocumentStatus.FAILED
        db.commit()
        db.refresh(db_document)
        print(f"Failed to process {filename}: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    return db_document

def get_document_metadata(db: Session, doc_id: int) -> models.Document:
    return db.query(models.Document).filter(models.Document.id == doc_id).first()