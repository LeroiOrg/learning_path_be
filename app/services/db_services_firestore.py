"""
Servicios de base de datos migrados a Firestore
learning_path_be

UPDATED: Now includes ACID transaction support
"""
from datetime import datetime
import uuid
from app.db.firestore_client import get_db
from app.db.transactions import FirestoreTransaction, with_retry
import logging

logger = logging.getLogger(__name__)

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


# ==================== ACID TRANSACTION FUNCTIONS ====================

@with_retry(max_attempts=3)
async def save_roadmap_with_conversation_atomic(
    user_email: str,
    roadmap_title: str,
    roadmap_content: dict,
    prompt: str,
    response: str,
    metadata: dict = None
) -> dict:
    """
    ACID Transaction: Saves roadmap and conversation atomically
    If either operation fails, both are rolled back
    
    This ensures data consistency - you'll never have orphaned roadmaps
    without their associated conversations
    
    Args:
        user_email: User's email
        roadmap_title: Title of the roadmap
        roadmap_content: Full roadmap data
        prompt: User's prompt that generated the roadmap
        response: AI response
        metadata: Optional metadata
    
    Returns:
        dict: Transaction result with success status and created document IDs
        
    Example:
        >>> result = await save_roadmap_with_conversation_atomic(
        ...     user_email="user@example.com",
        ...     roadmap_title="Python Developer Path",
        ...     roadmap_content={"steps": [...], "duration": "6 months"},
        ...     prompt="Create a Python roadmap",
        ...     response="Here's your roadmap..."
        ... )
    """
    session_id = get_or_create_session(user_email)
    timestamp = datetime.utcnow()
    
    # Prepare roadmap document
    roadmap_data = {
        "session_id": session_id,
        "user": user_email,
        "title": roadmap_title,
        "content": roadmap_content,
        "route": "/roadmaps",
        "timestamp": timestamp,
        "metadata": metadata or {}
    }
    
    # Prepare conversation document
    conversation_data = {
        "session_id": session_id,
        "user": user_email,
        "route": "/roadmaps",
        "prompt": prompt,
        "response": response,
        "metadata": {
            **(metadata or {}),
            "roadmap_title": roadmap_title,
            "roadmap_id": None  # Will be set after roadmap creation
        },
        "timestamp": timestamp
    }
    
    # Execute atomic transaction
    tx = FirestoreTransaction()
    operations = [
        {
            'type': 'create',
            'collection': 'roadmaps',
            'data': roadmap_data
        },
        {
            'type': 'create',
            'collection': 'conversations',
            'data': conversation_data
        }
    ]
    
    result = tx.execute(operations)
    
    if result['success']:
        # Now update the conversation with the roadmap_id
        roadmap_id = result['operations']['operation_0']['doc_id']
        conversation_id = result['operations']['operation_1']['doc_id']
        
        # Update conversation with roadmap_id
        db = get_db()
        db.collection('conversations').document(conversation_id).update({
            'metadata.roadmap_id': roadmap_id
        })
        
        logger.info(f"✅ ACID Transaction successful: Roadmap + Conversation saved for {user_email}")
        return {
            'success': True,
            'session_id': session_id,
            'roadmap_id': roadmap_id,
            'conversation_id': conversation_id,
            'timestamp': timestamp
        }
    else:
        logger.error(f"❌ ACID Transaction failed for {user_email}: {result.get('error')}")
        raise Exception(f"Transaction failed: {result.get('error')}")


@with_retry(max_attempts=3)
async def update_roadmap_with_log_atomic(
    roadmap_id: str,
    user_email: str,
    updates: dict,
    log_message: str
) -> dict:
    """
    ACID Transaction: Updates roadmap and creates a learning log atomically
    
    Args:
        roadmap_id: ID of the roadmap to update
        user_email: User's email
        updates: Dictionary of fields to update
        log_message: Log message describing the update
    
    Returns:
        dict: Transaction result
    """
    timestamp = datetime.utcnow()
    
    # Prepare update data
    update_data = {
        **updates,
        "updated_at": timestamp
    }
    
    # Prepare learning log
    log_data = {
        "user": user_email,
        "roadmap_id": roadmap_id,
        "message": log_message,
        "timestamp": timestamp,
        "changes": updates
    }
    
    # Execute atomic transaction
    tx = FirestoreTransaction()
    operations = [
        {
            'type': 'update',
            'collection': 'roadmaps',
            'doc_id': roadmap_id,
            'data': update_data
        },
        {
            'type': 'create',
            'collection': 'learning_logs',
            'data': log_data
        }
    ]
    
    result = tx.execute(operations)
    
    if result['success']:
        logger.info(f"✅ ACID Transaction successful: Roadmap updated + Log created for {roadmap_id}")
        return {
            'success': True,
            'roadmap_id': roadmap_id,
            'log_id': result['operations']['operation_1']['doc_id'],
            'timestamp': timestamp
        }
    else:
        logger.error(f"❌ ACID Transaction failed for roadmap {roadmap_id}: {result.get('error')}")
        raise Exception(f"Transaction failed: {result.get('error')}")


async def delete_roadmap_cascade_atomic(roadmap_id: str, user_email: str) -> dict:
    """
    ACID Transaction: Deletes roadmap and all associated conversations atomically
    
    Args:
        roadmap_id: ID of the roadmap to delete
        user_email: User's email (for verification)
    
    Returns:
        dict: Transaction result
    """
    try:
        db = get_db()
        
        # First, get all conversations associated with this roadmap
        conversations_query = (db.collection("conversations")
                             .where("user", "==", user_email)
                             .where("metadata.roadmap_id", "==", roadmap_id))
        
        conversation_docs = list(conversations_query.stream())
        
        # Build operations list
        operations = [
            {
                'type': 'delete',
                'collection': 'roadmaps',
                'doc_id': roadmap_id
            }
        ]
        
        # Add delete operations for all related conversations
        for conv_doc in conversation_docs:
            operations.append({
                'type': 'delete',
                'collection': 'conversations',
                'doc_id': conv_doc.id
            })
        
        # Execute atomic transaction
        tx = FirestoreTransaction()
        result = tx.execute(operations)
        
        if result['success']:
            logger.info(f"✅ ACID Transaction successful: Deleted roadmap {roadmap_id} and {len(conversation_docs)} conversations")
            return {
                'success': True,
                'roadmap_id': roadmap_id,
                'deleted_conversations': len(conversation_docs)
            }
        else:
            logger.error(f"❌ ACID Transaction failed for roadmap deletion: {result.get('error')}")
            raise Exception(f"Transaction failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Error in cascade delete: {e}")
        raise


# ==================== ORIGINAL FUNCTIONS (NON-TRANSACTIONAL) ====================

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
