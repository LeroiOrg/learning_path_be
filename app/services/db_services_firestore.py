"""
Servicios de base de datos migrados a Firestore
learning_path_be
"""
from datetime import datetime
import uuid
from app.db.firestore_client import get_db

# Cache en memoria para sesiones de usuarios
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
        db = get_db()
        # Crear documento en Firestore
        doc_ref = db.collection("conversations").document()
        doc_ref.set(data)
        
        print(f"✅ Conversación guardada correctamente en sesión {session_id} - Doc ID: {doc_ref.id}")
    except Exception as e:
        print(f"❌ Error al guardar conversación en Firestore: {e}")
        raise


async def get_conversations_by_user(user_email: str, limit: int = 10):
    """
    Obtiene las últimas conversaciones de un usuario desde Firestore.
    """
    try:
        print(f"🔍 Buscando conversaciones para: {user_email}")
        print(f"📊 Límite: {limit}")
        
        db = get_db()
        
        # Query en Firestore: filtrar por user y ordenar por timestamp descendente
        query = (db.collection("conversations")
                .where("user", "==", user_email)
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit))
        
        docs = query.stream()
        
        conversations = []
        for doc in docs:
            conv_dict = doc.to_dict()
            conv_dict["_id"] = doc.id  # Agregar el ID del documento
            
            # Convertir timestamp de Firestore a datetime si es necesario
            if hasattr(conv_dict.get("timestamp"), "timestamp"):
                conv_dict["timestamp"] = conv_dict["timestamp"].timestamp()
            
            conversations.append(conv_dict)
        
        print(f"✅ Conversaciones obtenidas: {len(conversations)}")
        return conversations
        
    except Exception as e:
        print(f"❌ Error al obtener conversaciones: {e}")
        return []


async def get_roadmaps_by_user(user_email: str, limit: int = 20):
    """
    Obtiene los roadmaps de un usuario (filtra por route='/roadmaps' ANTES de limitar).
    """
    try:
        print(f"📚 Buscando roadmaps para: {user_email}")
        
        db = get_db()
        
        # Query compuesto: filtrar por user Y route
        query = (db.collection("conversations")
                .where("user", "==", user_email)
                .where("route", "==", "/roadmaps")
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit))
        
        docs = query.stream()
        
        roadmaps = []
        for doc in docs:
            roadmap_dict = doc.to_dict()
            roadmap_dict["_id"] = doc.id
            
            # Convertir timestamp
            if hasattr(roadmap_dict.get("timestamp"), "timestamp"):
                roadmap_dict["timestamp"] = roadmap_dict["timestamp"].timestamp()
            
            roadmaps.append(roadmap_dict)
        
        print(f"✅ Roadmaps encontrados: {len(roadmaps)}")
        return roadmaps
        
    except Exception as e:
        print(f"❌ Error al obtener roadmaps: {e}")
        return []


# Funciones auxiliares adicionales

async def delete_conversation(conversation_id: str):
    """
    Elimina una conversación por su ID
    """
    try:
        db = get_db()
        db.collection("conversations").document(conversation_id).delete()
        print(f"✅ Conversación eliminada: {conversation_id}")
        return True
    except Exception as e:
        print(f"❌ Error eliminando conversación: {e}")
        return False


async def get_conversation_by_id(conversation_id: str):
    """
    Obtiene una conversación específica por su ID
    """
    try:
        db = get_db()
        doc = db.collection("conversations").document(conversation_id).get()
        
        if doc.exists:
            conv_dict = doc.to_dict()
            conv_dict["_id"] = doc.id
            return conv_dict
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo conversación: {e}")
        return None


async def count_user_conversations(user_email: str) -> int:
    """
    Cuenta el total de conversaciones de un usuario
    """
    try:
        db = get_db()
        query = db.collection("conversations").where("user", "==", user_email)
        docs = list(query.stream())
        count = len(docs)
        print(f"📊 Total de conversaciones para {user_email}: {count}")
        return count
    except Exception as e:
        print(f"❌ Error contando conversaciones: {e}")
        return 0


async def get_conversations_by_session(session_id: str):
    """
    Obtiene todas las conversaciones de una sesión específica
    """
    try:
        db = get_db()
        query = (db.collection("conversations")
                .where("session_id", "==", session_id)
                .order_by("timestamp"))
        
        docs = query.stream()
        
        conversations = []
        for doc in docs:
            conv_dict = doc.to_dict()
            conv_dict["_id"] = doc.id
            conversations.append(conv_dict)
        
        print(f"✅ Conversaciones de sesión {session_id}: {len(conversations)}")
        return conversations
        
    except Exception as e:
        print(f"❌ Error obteniendo conversaciones de sesión: {e}")
        return []
