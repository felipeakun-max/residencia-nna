from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.utils.auth import get_current_user

router = APIRouter()

def serial(doc):
    doc["id"] = str(doc.pop("_id"))
    return doc

class SeguimientoCreate(BaseModel):
    nna_id: str
    conducta: str
    actividades: str
    incidentes: Optional[str] = "Sin incidentes"
    observaciones: Optional[str] = None
    alerta_urgente: bool = False

@router.get("/")
async def get_seguimientos(nna_id: Optional[str] = None, user=Depends(get_current_user)):
    db = get_db()
    query = {}
    if nna_id: query["nna_id"] = nna_id
    if user["rol"] == "monitor": query["monitor_id"] = user["id"]
    cursor = db.seguimientos.find(query).sort("fecha", -1).limit(50)
    return [serial(s) async for s in cursor]

@router.post("/")
async def create_seguimiento(data: SeguimientoCreate, user=Depends(get_current_user)):
    db = get_db()
    doc = data.dict()
    doc["monitor_id"] = user["id"]
    doc["monitor_nombre"] = user["nombre"]
    doc["fecha"] = datetime.utcnow()
    result = await db.seguimientos.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc
