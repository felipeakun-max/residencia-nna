from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.utils.auth import verify_password, create_token, get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def login(data: LoginRequest):
    db = get_db()
    user = await db.usuarios.find_one({"email": data.email, "activo": True})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    
    token = create_token({
        "id": str(user["_id"]),
        "email": user["email"],
        "nombre": user["nombre"],
        "rol": user["rol"]
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "nombre": user["nombre"],
            "email": user["email"],
            "rol": user["rol"]
        }
    }

@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return current_user
