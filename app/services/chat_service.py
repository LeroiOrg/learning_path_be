# app/services/chat_service.py
from datetime import datetime
from typing import Optional
from bson import ObjectId
from app.database.mongodb import get_database
from app.models.chat_models import ChatConversation, Message
from app.services.ai_services import ask_gemini

async def start_chat_session(user_email: str, roadmap_topic: str) -> str:
    """
    Iniciar una nueva sesión de chat
    """
    db = get_database()
    
    # Verificar si ya existe una conversación activa para este usuario y tema
    existing_chat = await db.chat_conversations.find_one({
        "user_email": user_email,
        "roadmap_topic": roadmap_topic
    })
    
    if existing_chat:
        return str(existing_chat["_id"])
    
    # Crear nueva conversación
    new_chat = ChatConversation(
        user_email=user_email,
        roadmap_topic=roadmap_topic,
        conversation=[]
    )
    
    chat_dict = new_chat.dict(by_alias=True, exclude={"id"})
    result = await db.chat_conversations.insert_one(chat_dict)
    
    return str(result.inserted_id)

async def send_message(user_email: str, roadmap_topic: str, user_message: str) -> dict:
    """
    Enviar mensaje y obtener respuesta de IA
    """
    db = get_database()
    
    # Buscar o crear conversación
    chat_id = await start_chat_session(user_email, roadmap_topic)
    
    # Generar prompt contextualizado
    context_prompt = (
        f"Eres un tutor experto en {roadmap_topic}. El usuario te está preguntando: {user_message}. "
        f"Responde de manera educativa, clara y concisa. Si la pregunta no está relacionada con {roadmap_topic}, "
        f"redirige amablemente la conversación hacia el tema principal."
    )
    
    # Obtener respuesta de IA
    ai_response = await ask_gemini(context_prompt)
    
    # Crear nuevo mensaje
    new_message = Message(
        user_message=user_message,
        ai_response=ai_response
    )
    
    # Actualizar conversación en la base de datos
    await db.chat_conversations.update_one(
        {"_id": ObjectId(chat_id)},
        {
            "$push": {"conversation": new_message.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {
        "chat_id": chat_id,
        "user_message": user_message,
        "ai_response": ai_response,
        "timestamp": new_message.timestamp
    }

async def get_chat_history(user_email: str, roadmap_topic: str) -> Optional[dict]:
    # Obtener historial de chat
    db = get_database()
    
    chat = await db.chat_conversations.find_one({
        "user_email": user_email,
        "roadmap_topic": roadmap_topic
    })
    
    if not chat:
        return None
    
    chat["_id"] = str(chat["_id"])
    return chat