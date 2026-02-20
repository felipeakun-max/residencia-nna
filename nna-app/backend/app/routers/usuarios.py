from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.utils.auth import get_current_user, require_admin, hash_password

router = APIRouter()

def serial(doc):
    doc.pop("password_hash", None)
    doc["id"] = str(doc.pop("_id"))
    return doc

class UsuarioCreate(BaseModel):
    email: EmailStr
    nombre: str
    password: str
    rol: Literal["admin","profesional","monitor"]

@router.get("/")
async def get_usuarios(user=Depends(require_admin)):
    db = get_db()
    return [serial(u) async for u in db.usuarios.find()]

@router.post("/")
async def create_usuario(data: UsuarioCreate, user=Depends(require_admin)):
    db = get_db()
    existing = await db.usuarios.find_one({"email": data.email})
    if existing:
        raise HTTPException(400, "El correo ya está registrado")
    doc = {
        "email": data.email,
        "nombre": data.nombre,
        "rol": data.rol,
        "password_hash": hash_password(data.password),
        "activo": True,
        "fecha_creacion": datetime.utcnow()
    }
    result = await db.usuarios.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("password_hash")
    return doc

@router.put("/{user_id}/toggle")
async def toggle_usuario(user_id: str, user=Depends(require_admin)):
    db = get_db()
    u = await db.usuarios.find_one({"_id": ObjectId(user_id)})
    if not u: raise HTTPException(404, "Usuario no encontrado")
    await db.usuarios.update_one({"_id": ObjectId(user_id)}, {"$set": {"activo": not u["activo"]}})
    return {"ok": True}

@router.delete("/{user_id}")
async def delete_usuario(user_id: str, user=Depends(require_admin)):
    db = get_db()
    await db.usuarios.delete_one({"_id": ObjectId(user_id)})
    return {"ok": True}
