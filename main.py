from fastapi import FastAPI
from src.config import settings
from src.utils import csv

app = FastAPI(redoc_url=None, docs_url=None if settings.env == "prod" else "/docs")


@app.get("/")
def read_root():
    parents, subtasks = csv.load_and_filter("sample.csv")
    print(f"Parents: {len(parents)}, Subtasks: {len(subtasks)}")
    return {"Hello": "Root of Docusign Integration API"}