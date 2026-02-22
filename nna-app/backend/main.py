from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from app.routers import auth, nna, intervenciones, usuarios, seguimiento, talleres
app.include_router(auth.router, prefix="/api/auth")
app.include_router(nna.router, prefix="/api/nna")
app.include_router(intervenciones.router, prefix="/api/intervenciones")
app.include_router(usuarios.router, prefix="/api/usuarios")
app.include_router(seguimiento.router, prefix="/api/seguimiento")
app.include_router(talleres.router, prefix="/api/talleres")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def frontend():
    paths = [
        "/app/nna-app/frontend/gestion-nna.html",
        "/app/frontend/gestion-nna.html",
        os.path.join(os.path.dirname(__file__), "..", "frontend", "gestion-nna.html"),
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "gestion-nna.html"),
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                return HTMLResponse(f.read())
    # Mostrar rutas para debug
    import glob
    found = glob.glob("/app/**/*.html", recursive=True)
    return HTMLResponse(f"<h1>HTML no encontrado</h1><p>Buscado: {found}</p>")

