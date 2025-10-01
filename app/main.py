from fastapi import FastAPI
from app.api import learning_path_routes

app = FastAPI(title="Learning path Service", version="1.0")

app.include_router(learning_path_routes.router, prefix="/learning_path", tags=["learning_path"])

@app.get("/health")
def health():
    return {"status": "healthy"}
