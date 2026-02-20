from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date, datetime
from bson import ObjectId
from app.database import get_db
from app.utils.auth import get_current_user

router = APIRouter()

def serial(doc):
    doc["id"] = str(doc.pop("_id"))
    return doc

class NNACreate(BaseModel):
    nombre_completo: str
    rut: str
    fecha_nacimiento: date
    nacionalidad: str
    situacion_migratoria: Optional[str] = None
    fecha_ingreso: date
    escolaridad: str
    diagnostico: Optional[str] = None
    adulto_responsable: Optional[str] = None
    tribunal_derivante: Optional[str] = None
    estado: Literal["activo","egreso","suspension"] = "activo"
    observaciones: Optional[str] = None

class NNAUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    estado: Optional[str] = None
    escolaridad: Optional[str] = None
    diagnostico: Optional[str] = None
    observaciones: Optional[str] = None

@router.get("/")
async def get_nna(estado: Optional[str] = None, user=Depends(get_current_user)):
    db = get_db()
    query = {}
    if estado: query["estado"] = estado
    if user["rol"] == "monitor":
        query["profesional_id"] = user["id"]
    cursor = db.nna.find(query).sort("fecha_creacion", -1)
    return [serial(n) async for n in cursor]

@router.post("/")
async def create_nna(data: NNACreate, user=Depends(get_current_user)):
    if user["rol"] == "monitor":
        raise HTTPException(status_code=403, detail="Sin permisos para crear NNA")
    db = get_db()
    doc = data.dict()
    doc["fecha_nacimiento"] = doc["fecha_nacimiento"].isoformat()
    doc["fecha_ingreso"] = doc["fecha_ingreso"].isoformat()
    # Calcular edad
    hoy = date.today()
    nac = data.fecha_nacimiento
    doc["edad"] = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
    doc["profesional_id"] = user["id"]
    doc["profesional_nombre"] = user["nombre"]
    doc["fecha_creacion"] = datetime.utcnow()
    doc["nivel_riesgo"] = "bajo"
    result = await db.nna.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/{nna_id}")
async def get_one_nna(nna_id: str, user=Depends(get_current_user)):
    db = get_db()
    n = await db.nna.find_one({"_id": ObjectId(nna_id)})
    if not n: raise HTTPException(404, "NNA no encontrado")
    return serial(n)

@router.put("/{nna_id}")
async def update_nna(nna_id: str, data: NNAUpdate, user=Depends(get_current_user)):
    if user["rol"] == "monitor":
        raise HTTPException(403, "Sin permisos")
    db = get_db()
    update = {k: v for k, v in data.dict().items() if v is not None}
    update["fecha_modificacion"] = datetime.utcnow()
    await db.nna.update_one({"_id": ObjectId(nna_id)}, {"$set": update})
    return {"ok": True}

@router.delete("/{nna_id}")
async def delete_nna(nna_id: str, user=Depends(get_current_user)):
    if user["rol"] != "admin":
        raise HTTPException(403, "Solo administradores pueden eliminar")
    db = get_db()
    await db.nna.delete_one({"_id": ObjectId(nna_id)})
    return {"ok": True}
