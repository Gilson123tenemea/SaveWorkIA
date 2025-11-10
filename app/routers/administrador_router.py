from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.administrador_esquema import AdministradorCreate, LoginAdministrador
from app.servicios.administrador_servicio import crear_administrador, login_administrador

router = APIRouter(prefix="/administradores", tags=["Administrador"])

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/registrar")
def registrar_admin(request: AdministradorCreate, db: Session = Depends(get_db)):
    return crear_administrador(db, request)

@router.post("/login")
def login_admin(request: LoginAdministrador, db: Session = Depends(get_db)):
    return login_administrador(db, request)
