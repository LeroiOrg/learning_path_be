from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPBearer
from app.services.learning_path_services import (
    process_file_logic,
    generate_roadmap_logic,
    generate_questions_logic,
    related_topics_logic
)
from app.services.db_services import (
    save_conversation
)
from app.schemas.requests import (
    ProcessFileRequest,
    TopicRequest, 
)
from app.core.security import get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/documents")
async def process_file(
    request: ProcessFileRequest,
    email: dict = Depends(get_current_user),
    ):
    """
    Procesar un archivo y obtener las roadmaps
    """
    
    response = await process_file_logic(
        request
    )
    
    user_email = email["email"]
    
    await save_conversation(
        user_email=user_email,
        route="/documents",
        prompt=f"Procesar archivo: {request.fileName}",
        response=str(response)
    )
    
    return response


@router.post("/roadmaps")
async def generate_roadmap(
    request: TopicRequest,
    email: dict = Depends(get_current_user)
    ):
    """
    Generar una roadmap a partir de los temas
    """
    response = await generate_roadmap_logic(request, email["email"])
    
    user_email = email["email"]
    
    await save_conversation(
        user_email=user_email,
        route="/roadmaps",
        prompt=f"Generar roadmap del tema: {request.topic}",
        response=str(response)
    )
    
    return response
    
@router.post("/questions")
async def generate_questions(
    request: TopicRequest,
    email: dict = Depends(get_current_user)
    ):
    """
    Generar un conjunto de preguntas a partir del contenido de los temas relacionados
    """
    response = await generate_questions_logic(request)
    
    user_email = email["email"]
    
    await save_conversation(
        user_email=user_email,
        route="/questions",
        prompt=f"Generar preguntas del tema: {request.topic}",
        response=str(response)
    )
    
    return response 

@router.post("/related-topics")
async def related_topics(
    request: TopicRequest,
    email: dict = Depends(get_current_user)
    ):
    """
    Obtener temas relacionados a un tema principal
    """
    response = await related_topics_logic(request)
    
    user_email = email["email"]
    
    await save_conversation(
        user_email=user_email,
        route="/related-topics",
        prompt=f"Buscar temas relacionados con: {request.topic}",
        response=str(response)
    )
    
    return response
