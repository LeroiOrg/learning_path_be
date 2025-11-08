"""
Servicios de base de datos - Migrado a Firestore
Mantiene compatibilidad con código existente
"""
from app.services.db_services_firestore import (
    get_or_create_session,
    save_conversation,
    get_conversations_by_user,
    get_roadmaps_by_user,
    delete_conversation,
    get_conversation_by_id,
    count_user_conversations,
    get_conversations_by_session
)

# Re-exportar todas las funciones para mantener compatibilidad
__all__ = [
    'get_or_create_session',
    'save_conversation',
    'get_conversations_by_user',
    'get_roadmaps_by_user',
    'delete_conversation',
    'get_conversation_by_id',
    'count_user_conversations',
    'get_conversations_by_session'
]
