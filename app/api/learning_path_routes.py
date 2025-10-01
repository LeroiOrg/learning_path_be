from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from app.services.learning_path_services import (
    process_file_logic,
    generate_roadmap_logic,
    generate_questions_logic
)
from app.schemas.requests import (
    ProcessFileRequest,
    TopicRequest, 
)
from app.core.security import get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/process-file")
async def process_file(
    request: ProcessFileRequest,
    email: str = Depends(get_current_user),
    ):
    """
    Procesar un archivo y obtener las roadmaps
    """
    
    response = await process_file_logic(
        request, credits=3
    )
    return response


@router.post("/generate-roadmap")
async def generate_roadmap(
    request: TopicRequest,
    email: str = Depends(get_current_user)
    ):
    """
    Generar una roadmap a partir de los temas
    """
    return await generate_roadmap_logic(request)
    
@router.post("/generate-questions")
async def generate_questions(
    request: TopicRequest,
    email: str = Depends(get_current_user)
    ):
    """
    Generar un conjunto de preguntas a partir del contenido de los temas relacionados
    """
    return await generate_questions_logic(request)