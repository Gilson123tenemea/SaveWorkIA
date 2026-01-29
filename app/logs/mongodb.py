from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                # Leer desde variables de entorno
                MONGO_URI = os.getenv("MONGO_URI")
                MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

                if not MONGO_URI or not MONGO_DB_NAME:
                    raise Exception("Variables MongoDB no definidas")

                cls._client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                cls._db = cls._client[MONGO_DB_NAME]

                # Verificar conexión
                cls._client.admin.command("ping")
                print("✅ Conexión a MongoDB exitosa")

            except ConnectionFailure as e:
                print(f"❌ Error conectando a MongoDB: {e}")
                raise

        return cls._db

    @classmethod
    def close_connection(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None


def get_mongodb():
    return MongoDB.get_client()