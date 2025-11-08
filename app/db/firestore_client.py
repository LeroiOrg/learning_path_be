"""
Módulo de conexión a Google Cloud Firestore
Reemplaza la conexión anterior de MongoDB
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
IS_PRODUCTION = os.getenv("NODE_ENV") == "production" or os.getenv("K_SERVICE") is not None

# Cliente de Firestore (singleton)
_db: Optional[firestore.Client] = None


def initialize_firestore() -> firestore.Client:
    """
    Inicializa la conexión a Firestore usando el service account en desarrollo
    o Application Default Credentials en producción (Cloud Run)
    Solo se ejecuta una vez (patrón singleton)
    """
    global _db
    
    if _db is not None:
        return _db
    
    try:
        # Verificar si ya está inicializado
        if not firebase_admin._apps:
            if IS_PRODUCTION:
                # En producción (Cloud Run), usar Application Default Credentials
                firebase_admin.initialize_app(options={
                    'projectId': PROJECT_ID,
                })
                print(f"✅ Firebase Admin SDK inicializado para proyecto: {PROJECT_ID} (Production - ADC)")
            else:
                # En desarrollo, usar archivo JSON de credenciales
                if not os.path.exists(CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        f"❌ Archivo de credenciales no encontrado en: {CREDENTIALS_PATH}\n"
                        f"   Asegúrate de colocar service-account.json en la carpeta /keys/"
                    )
                
                cred = credentials.Certificate(CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'projectId': PROJECT_ID,
                })
                print(f"✅ Firebase Admin SDK inicializado para proyecto: {PROJECT_ID} (Development)")
        
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
    """Nombres de las colecciones en Firestore para learning path"""
    CONVERSATIONS = "conversations"
    USER_SESSIONS = "user_sessions"
    ROADMAPS = "roadmaps"
    LEARNING_LOGS = "learning_logs"


# Inicializar automáticamente al importar el módulo
try:
    initialize_firestore()
except Exception as e:
    print(f"⚠️  Advertencia: No se pudo inicializar Firestore al importar: {e}")
