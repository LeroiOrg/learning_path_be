from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import ai_routes, chat_routes
from app.database.mongodb import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title="IA Service", version="1.0", lifespan=lifespan)

app.include_router(ai_routes.router, prefix="/ai", tags=["ai"])
app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])

@app.get("/health")
def health():
    return {"status": "healthy"}