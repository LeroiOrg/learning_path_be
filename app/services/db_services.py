from datetime import datetime
import uuid
from app.db.mongo_client import db

conversations_collection = db["conversations"]
_user_sessions = {}

def get_or_create_session(user_email: str) -> str:
    """
    Retorna el session_id actual de un usuario o crea uno nuevo si no existe.
    Permite agrupar todas las conversaciones del usuario en una misma sesión.
    """
    if user_email not in _user_sessions:
        session_id = str(uuid.uuid4()) 
        _user_sessions[user_email] = session_id
        print(f"🆕 Nueva sesión creada para {user_email}: {session_id}")
    else:
        session_id = _user_sessions[user_email]
    return session_id


async def save_conversation(
    user_email: str,
    route: str,
    prompt: str,
    response: str,
    metadata: dict = None
):
    """
    Guarda una conversación asociada a un usuario y sesión activa.
    Si el usuario no tiene sesión activa, se genera un session_id.
    """
    session_id = get_or_create_session(user_email)

    data = {
        "session_id": session_id,
        "user": user_email,
        "route": route,
        "prompt": prompt,
        "response": response,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow()
    }

    try:
        conversations_collection.insert_one(data)
        print(f"Conversación guardada correctamente en sesión {session_id}")
    except Exception as e:
        print("Error al guardar conversación en MongoDB:", e)


async def get_conversations_by_user(user_email: str, limit: int = 10):
    """
    Obtiene las últimas conversaciones de un usuario desde MongoDB.
    """
    try:
        conversations = list(
            conversations_collection.find({"user": user_email})
            .sort("timestamp", -1)
            .limit(limit)
        )
        for c in conversations:
            c["_id"] = str(c["_id"])  
        return conversations
    except Exception as e:
        print("Error al obtener conversaciones:", e)
        return []
