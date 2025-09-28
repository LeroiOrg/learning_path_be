from fastapi import APIRouter, Depends, HTTPException
from app.services.chat_service import start_chat_session, send_message, get_chat_history
from app.schemas.requests import ChatRequest, StartChatRequest
from app.core.security import get_current_user

router = APIRouter()

@router.post("/start-chat")
async def start_chat(
    request: StartChatRequest,
    email: str = Depends(get_current_user)
):
    # Iniciar una nueva sesión de chat o recuperar una existente
    try:
        chat_id = await start_chat_session(email, request.roadmap_topic)
        return {
            "chat_id": chat_id,
            "roadmap_topic": request.roadmap_topic,
            "message": "Sesión de chat iniciada. ¿Qué te gustaría saber sobre este tema?"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar chat: {str(e)}")

@router.post("/send-message")
async def send_chat_message(
    request: ChatRequest,
    email: str = Depends(get_current_user)
):
    # Enviar mensaje y recibir respuesta de IA
    try:
        response = await send_message(email, request.roadmap_topic, request.user_message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar mensaje: {str(e)}")

@router.get("/chat-history/{roadmap_topic}")
async def get_conversation_history(
    roadmap_topic: str,
    email: str = Depends(get_current_user)
):
    # Obtener historial completo de la conversación
    try:
        history = await get_chat_history(email, roadmap_topic)
        if not history:
            return {"message": "No se encontró historial para este tema"}
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")