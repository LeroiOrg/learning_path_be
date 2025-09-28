import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    mongodb.database = mongodb.client[os.getenv("DATABASE_NAME")]
    print("Conectado a MongoDB")

async def close_mongo_connection():
    mongodb.client.close()
    print("Conexión a MongoDB cerrada")

def get_database():
    return mongodb.database