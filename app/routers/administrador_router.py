from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.administrador_esquema import AdministradorCreate, AdministradorResponse
from app.servicios import administrador_servicio

router = APIRouter(prefix="/administradores", tags=["Administradores"])

# Dependencia de sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AdministradorResponse)
def crear_administrador(administrador: AdministradorCreate, db: Session = Depends(get_db)):
    return administrador_servicio.crear_administrador(db, administrador)

@router.get("/", response_model=list[AdministradorResponse])
def listar_administradores(db: Session = Depends(get_db)):
    return administrador_servicio.obtener_administradores(db)

@router.get("/{admin_id}", response_model=AdministradorResponse)
def obtener_administrador(admin_id: int, db: Session = Depends(get_db)):
    return administrador_servicio.obtener_administrador_por_id(db, admin_id)
