from fastapi import FastAPI
from app.api import ai_routes

app = FastAPI(title="IA Service", version="1.0")

app.include_router(ai_routes.router, prefix="/ai", tags=["ai"])

@app.get("/health")
def health():
    return {"status": "healthy"}
