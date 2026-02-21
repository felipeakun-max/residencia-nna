import motor.motor_asyncio
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "residencia_nna")

client = None
db = None

async def connect_db():
    global client, db
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGO_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
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
    except Exception as e:
        print(f"⚠️ MongoDB no disponible al inicio: {e}")
        print("El servidor continuará — reintentará al recibir peticiones")

async def close_db():
    if client:
        client.close()

def get_db():
    if db is None:
        raise Exception("Base de datos no conectada")
    return db
