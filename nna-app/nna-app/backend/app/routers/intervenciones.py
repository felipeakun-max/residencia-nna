from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.utils.auth import get_current_user

router = APIRouter()

def serial(doc):
    doc["id"] = str(doc.pop("_id"))
    return doc

class IntervencionCreate(BaseModel):
    nna_id: str
    tipo: Literal["psicosocial","educativa","familiar","judicial","salud"]
    descripcion: str
    acuerdos: Optional[str] = None
    proximos_pasos: Optional[str] = None
    nivel_riesgo: Literal["bajo","medio","alto"] = "bajo"

@router.get("/")
async def get_intervenciones(nna_id: Optional[str] = None, user=Depends(get_current_user)):
    db = get_db()
    query = {}
    if nna_id: query["nna_id"] = nna_id
    if user["rol"] == "monitor": query["profesional_id"] = user["id"]
    cursor = db.intervenciones.find(query).sort("fecha", -1)
    return [serial(i) async for i in cursor]

@router.post("/")
async def create_intervencion(data: IntervencionCreate, user=Depends(get_current_user)):
    if user["rol"] == "monitor":
        raise HTTPException(403, "Sin permisos para registrar intervenciones")
    db = get_db()
    doc = data.dict()
    doc["profesional_id"] = user["id"]
    doc["profesional_nombre"] = user["nombre"]
    doc["fecha"] = datetime.utcnow()
    result = await db.intervenciones.insert_one(doc)
    # Actualizar nivel de riesgo del NNA
    await db.nna.update_one(
        {"_id": ObjectId(data.nna_id)},
        {"$set": {"nivel_riesgo": data.nivel_riesgo, "ultima_intervencion": datetime.utcnow()}}
    )
    doc["id"] = str(result.inserted_id)
    return doc

@router.delete("/{int_id}")
async def delete_intervencion(int_id: str, user=Depends(get_current_user)):
    if user["rol"] != "admin":
        raise HTTPException(403, "Solo administradores")
    db = get_db()
    await db.intervenciones.delete_one({"_id": ObjectId(int_id)})
    return {"ok": True}
