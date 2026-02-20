from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, nna, intervenciones, usuarios, seguimiento
from app.database import connect_db, close_db

app = FastAPI(title="Gestión Residencia NNA", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup(): await connect_db()

@app.on_event("shutdown")
async def shutdown(): await close_db()

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(nna.router, prefix="/api/nna", tags=["NNA"])
app.include_router(intervenciones.router, prefix="/api/intervenciones", tags=["Intervenciones"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(seguimiento.router, prefix="/api/seguimiento", tags=["Seguimiento"])

@app.get("/")
async def root():
    return {"status": "ok", "app": "Gestión Residencia NNA"}
