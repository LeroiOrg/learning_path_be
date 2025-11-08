"""
Módulo de cliente de base de datos
Migrado de MongoDB a Firestore
"""
from app.db.firestore_client import get_db, Collections

# Cliente principal
db = get_db()

# Para mantener compatibilidad con código existente que usa "db"
# Ahora db es un cliente de Firestore en lugar de MongoDB

print(f"🔌 FIRESTORE configurado - Cliente disponible: {type(db)}")
