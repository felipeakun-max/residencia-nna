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
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        db = client[DB_NAME]
        from passlib.context import CryptContext
        pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
        existing = await db.usuarios.find_one({"email": "admin@residencia.cl"})
        if not existing:
            await db.usuarios.insert_one({
                "email": "admin@residencia.cl",
                "nombre": "Administrador",
                "rol": "admin",
                "password_hash": pwd.hash("admin123"),
                "activo": True
            })
            print("✅ Admin creado")
        print("✅ MongoDB conectado")
    except Exception as e:
        print(f"⚠️ Error: {e}")

async def close_db():
    if client:
        client.close()

def get_db():
    if db is None:
        raise Exception("Base de datos no conectada")
    return db
