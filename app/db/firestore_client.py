"""
Módulo de conexión a Google Cloud Firestore
Cliente para learning_path_be
"""
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional

# Cargar variables de entorno
load_dotenv()

# Variables de configuración
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "leroi-474015")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./keys/service-account.json")

# Cliente de Firestore (singleton)
_db: Optional[firestore.Client] = None


def initialize_firestore() -> firestore.Client:
    """
    Inicializa la conexión a Firestore usando el service account
    Solo se ejecuta una vez (patrón singleton)
    """
    global _db
    
    if _db is not None:
        return _db
    
    try:
        # Verificar que el archivo de credenciales existe
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(
                f"❌ Archivo de credenciales no encontrado en: {CREDENTIALS_PATH}\n"
                f"   Asegúrate de colocar service-account.json en la carpeta /keys/"
            )
        
        # Inicializar Firebase Admin SDK
        cred = credentials.Certificate(CREDENTIALS_PATH)
        
        # Verificar si ya está inicializado (importante para múltiples instancias)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'projectId': PROJECT_ID,
            })
            print(f"✅ Firebase Admin SDK inicializado para proyecto: {PROJECT_ID}")
        
        # Crear cliente de Firestore
        _db = firestore.client()
        print(f"✅ Conexión a Firestore exitosa - Proyecto: {PROJECT_ID}")
        
        return _db
        
    except Exception as e:
        print(f"❌ Error al conectar a Firestore: {e}")
        raise


def get_db() -> firestore.Client:
    """
    Obtiene el cliente de Firestore
    Si no está inicializado, lo inicializa
    
    Returns:
        firestore.Client: Cliente de Firestore
    """
    if _db is None:
        return initialize_firestore()
    return _db


# Colecciones disponibles en esta base de datos
class Collections:
    """Nombres de las colecciones en Firestore para learning paths"""
    ROADMAPS = "roadmaps"
    USER_PROGRESS = "user_progress"
    LEARNING_RESOURCES = "learning_resources"
    TOPICS = "topics"
    USER_GOALS = "user_goals"


# Inicializar automáticamente al importar el módulo
try:
    initialize_firestore()
    print(f"🔌 FIRESTORE configurado correctamente")
except Exception as e:
    print(f"⚠️  Advertencia: No se pudo inicializar Firestore al importar: {e}")
