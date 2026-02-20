import motor.motor_asyncio
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "residencia_nna")

client = None
db = None

async def connect_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    # Crear usuario admin por defecto si no existe
    from app.utils.auth import hash_password
    existing = await db.usuarios.find_one({"email": "admin@residencia.cl"})
    if not existing:
        await db.usuarios.insert_one({
            "email": "admin@residencia.cl",
            "nombre": "Administrador",
            "rol": "admin",
            "password_hash": hash_password("admin123"),
            "activo": True
        })
    print("✅ Base de datos conectada")

async def close_db():
    if client:
        client.close()

def get_db():
    return db
