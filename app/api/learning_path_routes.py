from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from app.services.learning_path_services import (
    process_file_logic,
    generate_roadmap_logic,
    generate_questions_logic,
    related_topics_logic
)
from app.schemas.requests import (
    ProcessFileRequest,
    TopicRequest, 
)
from app.core.security import get_current_user
import json

router = APIRouter()
security = HTTPBearer()

@router.post("/documents")
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


@router.post("/roadmaps")
async def generate_roadmap(
    request: TopicRequest,
    email: str = Depends(get_current_user)
    ):
    """
    Generar una roadmap a partir de los temas
    """
    return await generate_roadmap_logic(request)
    
@router.post("/questions")
async def generate_questions(
    request: TopicRequest,
    email: str = Depends(get_current_user)
    ):
    """
    Generar un conjunto de preguntas a partir del contenido de los temas relacionados
    """
    return await generate_questions_logic(request)

@router.post("/related-topics")
async def related_topics(request: TopicRequest):
    """
    Obtener temas relacionados a un tema principal
    """
    print("Se van a obtener temas relacionados")
    full_prompt = (
        f"Eres un experto en la generación de temas relacionados a un tema principal. El tema principal es {request.topic}. Quiero que el formato de la respuesta sea una"
        f"lista con únicamente MÁXIMO 6 temas relacionados y NADA MÁS, es decir: [\"tema1\", \"tema2\", \"tema3\"] "
        f"Y que ademas, Cada tema debe tener una longitud máxima de 45 caracteres.  "
    )
    response, tokens = await ask_gemini(full_prompt)
    parse_resposne = response.replace("json", "").replace("```", "")
    print("parseado:", parse_resposne)
    return parse_resposne
