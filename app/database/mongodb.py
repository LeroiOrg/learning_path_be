import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("DATABASE_NAME")
    
    if not mongodb_uri or not database_name:
        print("ERROR: Faltan variables MONGODB_URI o DATABASE_NAME en .env")
        return
    
    mongodb.client = AsyncIOMotorClient(mongodb_uri)
    mongodb.database = mongodb.client[database_name]
    print(f"Conectado a MongoDB - Database: {database_name}")

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("Conexión a MongoDB cerrada")

def get_database():
    return mongodb.database