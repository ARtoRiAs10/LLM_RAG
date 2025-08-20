from fastapi import FastAPI
from app.core.config import settings
from app.api import endpoints
from app.models import models, database

# This command connects to the NeonDB database via the engine
# and creates the 'documents' table if it doesn't already exist.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json"
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}