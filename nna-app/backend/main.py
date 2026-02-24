from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
import urllib.request

@asynccontextmanager
async def lifespan(app: FastAPI):
await connect_db()
yield
await close_db()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=[”*”],
allow_headers=[”*”],
)

from app.routers import auth, nna, intervenciones, usuarios, seguimiento, talleres
app.include_router(auth.router, prefix=”/api/auth”)
app.include_router(nna.router, prefix=”/api/nna”)
app.include_router(intervenciones.router, prefix=”/api/intervenciones”)
app.include_router(usuarios.router, prefix=”/api/usuarios”)
app.include_router(seguimiento.router, prefix=”/api/seguimiento”)
app.include_router(talleres.router, prefix=”/api/talleres”)

@app.get(”/health”)
async def health():
return {“status”: “ok”}

@app.get(”/setup”)
async def setup():
from passlib.context import CryptContext
from app.database import get_db
pwd = CryptContext(schemes=[“bcrypt”], deprecated=“auto”)
db = get_db()
await db.usuarios.delete_many({“email”: “admin@residencia.cl”})
await db.usuarios.insert_one({
“email”: “admin@residencia.cl”,
“nombre”: “Administrador”,
“rol”: “admin”,
“password_hash”: pwd.hash(“admin123”),
“activo”: True
})
return {“ok”: “Usuario admin creado exitosamente”}

@app.get(”/”)
async def frontend():
try:
url = “https://raw.githubusercontent.com/felipeakun-max/residencia-nna/main/nna-app/frontend/gestion-nna.html”
with urllib.request.urlopen(url, timeout=10) as r:
return HTMLResponse(r.read().decode(“utf-8”))
except Exception as e:
return HTMLResponse(f”<h1>Error: {e}</h1>”)
