from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

print(f"🔌 MONGO_URI configurada: {MONGO_URI[:50]}..." if MONGO_URI else "❌ MONGO_URI no encontrada")

if not MONGO_URI:
    raise ValueError("MONGO_URI no está configurada en las variables de entorno")

client = MongoClient(MONGO_URI)
db = client["leroi_learning"]

# Verificar conexión
try:
    client.admin.command('ping')
    print("✅ Conectado a MongoDB Atlas correctamente")
except Exception as e:
    print(f"❌ Error conectando a MongoDB: {e}")
