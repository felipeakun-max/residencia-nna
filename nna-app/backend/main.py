from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import connect_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(title="Gestión Residencia NNA", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import auth, nna, intervenciones, usuarios, seguimiento, talleres
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(nna.router, prefix="/api/nna", tags=["NNA"])
app.include_router(intervenciones.router, prefix="/api/intervenciones", tags=["Intervenciones"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(seguimiento.router, prefix="/api/seguimiento", tags=["Seguimiento"])
app.include_router(talleres.router, prefix="/api/talleres", tags=["Talleres"])

@app.get("/")
async def root():
    return {"status": "ok", "app": "Gestión Residencia NNA v2.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}
