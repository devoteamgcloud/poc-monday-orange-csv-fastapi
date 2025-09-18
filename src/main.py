from fastapi import FastAPI

from src.config import settings
from src.routers import sync

app = FastAPI(redoc_url=None, docs_url=None if settings.env == "prod" else "/docs")

app.include_router(sync.router, tags=["sync"])

@app.get("/")
def read_root():
    return {"Hello": "Sync service is healthy"}
