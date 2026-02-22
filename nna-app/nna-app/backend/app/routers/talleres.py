from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.utils.auth import get_current_user
import os, aiofiles, uuid

router = APIRouter()
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def serial(doc):
    doc["id"] = str(doc.pop("_id"))
    return doc

# ─── MODELOS ─────────────────────────────────────────────

class Diapositiva(BaseModel):
    titulo: str
    contenido: str
    orden: int

class Material(BaseModel):
    tipo: Literal["guia","ficha","evaluacion","checklist"]
    titulo: str
    contenido: str

class Actividad(BaseModel):
    nombre: str
    descripcion: str
    tiempo_estimado: int
    tipo: str

class TallerCreate(BaseModel):
    titulo: str
    area: Literal["parentalidad","autocuidado","empleabilidad","educacion","salud","otro"]
    objetivo_general: str
    objetivos_especificos: Optional[List[str]] = []
    duracion_minutos: int
    materiales: Optional[List[str]] = []
    poblacion_objetivo: str
    descripcion: str
    diapositivas: Optional[List[Diapositiva]] = []
    actividades: Optional[List[Actividad]] = []
    material_imprimible: Optional[List[Material]] = []

class TallerUpdate(BaseModel):
    titulo: Optional[str] = None
    area: Optional[str] = None
    objetivo_general: Optional[str] = None
    descripcion: Optional[str] = None
    duracion_minutos: Optional[int] = None
    poblacion_objetivo: Optional[str] = None

class EjecucionCreate(BaseModel):
    taller_id: str
    fecha: str
    lugar: Optional[str] = None
    observaciones: Optional[str] = None
    asistentes: List[dict]  # [{nna_id, nna_nombre, presente: bool, observacion}]

# ─── PLANTILLAS (Templates) ───────────────────────────────

@router.get("/plantillas")
async def get_plantillas(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.talleres.find({}).sort("fecha_creacion", -1)
    return [serial(t) async for t in cursor]

@router.post("/plantillas")
async def create_plantilla(data: TallerCreate, user=Depends(get_current_user)):
    if user["rol"] == "monitor":
        raise HTTPException(403, "Sin permisos para crear talleres")
    db = get_db()
    doc = data.dict()
    doc["creado_por"] = user["nombre"]
    doc["creado_por_id"] = user["id"]
    doc["fecha_creacion"] = datetime.utcnow()
    doc["archivos"] = []
    doc["total_ejecuciones"] = 0
    result = await db.talleres.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/plantillas/{taller_id}")
async def get_plantilla(taller_id: str, user=Depends(get_current_user)):
    db = get_db()
    t = await db.talleres.find_one({"_id": ObjectId(taller_id)})
    if not t: raise HTTPException(404, "Taller no encontrado")
    return serial(t)

@router.put("/plantillas/{taller_id}")
async def update_plantilla(taller_id: str, data: TallerUpdate, user=Depends(get_current_user)):
    if user["rol"] == "monitor":
        raise HTTPException(403, "Sin permisos")
    db = get_db()
    update = {k: v for k, v in data.dict().items() if v is not None}
    await db.talleres.update_one({"_id": ObjectId(taller_id)}, {"$set": update})
    return {"ok": True}

@router.delete("/plantillas/{taller_id}")
async def delete_plantilla(taller_id: str, user=Depends(get_current_user)):
    if user["rol"] != "admin":
        raise HTTPException(403, "Solo administradores")
    db = get_db()
    await db.talleres.delete_one({"_id": ObjectId(taller_id)})
    return {"ok": True}

# ─── ARCHIVOS ADJUNTOS ────────────────────────────────────

@router.post("/plantillas/{taller_id}/archivos")
async def upload_archivo(
    taller_id: str,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    allowed = [".pdf", ".pptx", ".docx", ".doc"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Tipo no permitido. Use: {', '.join(allowed)}")
    
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    archivo = {
        "id": str(uuid.uuid4()),
        "nombre_original": file.filename,
        "filename": filename,
        "tipo": ext.replace(".", ""),
        "subido_por": user["nombre"],
        "fecha_subida": datetime.utcnow().isoformat()
    }
    
    db = get_db()
    await db.talleres.update_one(
        {"_id": ObjectId(taller_id)},
        {"$push": {"archivos": archivo}}
    )
    return archivo

@router.delete("/plantillas/{taller_id}/archivos/{archivo_id}")
async def delete_archivo(taller_id: str, archivo_id: str, user=Depends(get_current_user)):
    db = get_db()
    await db.talleres.update_one(
        {"_id": ObjectId(taller_id)},
        {"$pull": {"archivos": {"id": archivo_id}}}
    )
    return {"ok": True}

# ─── EJECUCIONES (Instances) ──────────────────────────────

@router.get("/ejecuciones")
async def get_ejecuciones(taller_id: Optional[str] = None, user=Depends(get_current_user)):
    db = get_db()
    query = {}
    if taller_id: query["taller_id"] = taller_id
    cursor = db.ejecuciones_taller.find(query).sort("fecha", -1)
    return [serial(e) async for e in cursor]

@router.post("/ejecuciones")
async def create_ejecucion(data: EjecucionCreate, user=Depends(get_current_user)):
    if user["rol"] == "monitor":
        raise HTTPException(403, "Sin permisos para ejecutar talleres")
    db = get_db()
    
    # Obtener info del taller
    taller = await db.talleres.find_one({"_id": ObjectId(data.taller_id)})
    if not taller: raise HTTPException(404, "Taller no encontrado")
    
    doc = data.dict()
    doc["taller_titulo"] = taller["titulo"]
    doc["taller_area"] = taller["area"]
    doc["profesional_id"] = user["id"]
    doc["profesional_nombre"] = user["nombre"]
    doc["fecha_registro"] = datetime.utcnow()
    
    result = await db.ejecuciones_taller.insert_one(doc)
    ejecucion_id = str(result.inserted_id)
    
    # Crear intervención automática para cada asistente presente
    for asistente in data.asistentes:
        if asistente.get("presente"):
            intervencion = {
                "nna_id": asistente["nna_id"],
                "tipo": "educativa",
                "descripcion": f"Participación en taller: {taller['titulo']}. Área: {taller['area']}. {asistente.get('observacion', '')}",
                "acuerdos": None,
                "proximos_pasos": None,
                "nivel_riesgo": "bajo",
                "profesional_id": user["id"],
                "profesional_nombre": user["nombre"],
                "fecha": datetime.utcnow(),
                "fecha_creacion": datetime.utcnow(),
                "origen": "taller",
                "taller_id": data.taller_id,
                "ejecucion_id": ejecucion_id,
                "taller_titulo": taller["titulo"]
            }
            await db.intervenciones.insert_one(intervencion)
    
    # Actualizar contador de ejecuciones del taller
    await db.talleres.update_one(
        {"_id": ObjectId(data.taller_id)},
        {"$inc": {"total_ejecuciones": 1}}
    )
    
    doc["id"] = ejecucion_id
    return doc

@router.get("/ejecuciones/{ejecucion_id}")
async def get_ejecucion(ejecucion_id: str, user=Depends(get_current_user)):
    db = get_db()
    e = await db.ejecuciones_taller.find_one({"_id": ObjectId(ejecucion_id)})
    if not e: raise HTTPException(404, "Ejecución no encontrada")
    return serial(e)
