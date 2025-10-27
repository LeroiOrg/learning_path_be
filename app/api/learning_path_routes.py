from fastapi import APIRouter, Depends, Response, HTTPException, Header
from fastapi.security import HTTPBearer
from typing import Optional
from app.services.learning_path_services import (
    process_file_logic,
    generate_roadmap_logic,
    generate_questions_logic,
    related_topics_logic
)
from app.services.db_services import (
    save_conversation,
    get_conversations_by_user,
    get_roadmaps_by_user
)
from app.schemas.requests import (
    ProcessFileRequest,
    TopicRequest, 
)
from app.core.security import get_current_user
import os

router = APIRouter()
security = HTTPBearer()

# Key para servicios internos
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "internal_service_key_123")

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


@router.get("/roadmaps/user/{user_email}")
async def get_user_roadmaps(
    user_email: str,
    limit: int = 20,
    x_api_key: Optional[str] = Header(None)
):
    """
    Obtener todos los roadmaps de un usuario
    Permite acceso con API key para servicios internos
    """
    # Verificar si viene con API key de servicio interno
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # Usar nueva función que filtra primero
        roadmaps = await get_roadmaps_by_user(user_email, limit)
        
        return {
            "success": True,
            "count": len(roadmaps),
            "data": roadmaps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roadmaps/user/{user_email}/latest")
async def get_latest_roadmap(
    user_email: str,
    x_api_key: Optional[str] = Header(None)
):
    """
    Obtener el último roadmap generado por un usuario
    Permite acceso con API key para servicios internos
    """
    # Verificar si viene con API key de servicio interno
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        roadmaps = await get_roadmaps_by_user(user_email, limit=1)
        
        if not roadmaps:
            return {
                "success": False,
                "message": "No roadmaps found for this user"
            }
        
        return {
            "success": True,
            "data": roadmaps[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
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
