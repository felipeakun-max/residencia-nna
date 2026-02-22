from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
import os

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

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/api")
async def api_root():
    return {"status": "ok", "app": "Gestión Residencia NNA v2.0"}

@app.get("/")
async def serve_frontend():
    # Buscar el HTML en varias rutas posibles
    paths = [
        "/app/frontend/gestion-nna.html",
        "../frontend/gestion-nna.html", 
        "../../frontend/gestion-nna.html",
        "/app/nna-app/frontend/gestion-nna.html"
    ]
    for path in paths:
        if os.path.exists(path):
            return FileResponse(path, media_type="text/html")
    
    # Si no encuentra el archivo, devolver página con instrucciones
    return HTMLResponse("""
    <html><body style="font-family:sans-serif;padding:40px;background:#0f1b2d;color:white;">
    <h1>✅ Backend funcionando</h1>
    <p>API disponible en <a href="/docs" style="color:#4fa3ff">/docs</a></p>
    </body></html>
    """)
