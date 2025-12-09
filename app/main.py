from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import learning_path_routes
import os
import uvicorn 

app = FastAPI(title="Learning path Service", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(learning_path_routes.router, prefix="/learning_path", tags=["learning_path"])

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080)) 
    uvicorn.run(app, host="0.0.0.0", port=port)
