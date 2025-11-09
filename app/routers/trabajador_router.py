from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.trabajador_esquema import TrabajadorCreate, TrabajadorResponse
from app.servicios import trabajador_servicio

router = APIRouter(prefix="/trabajadores", tags=["Trabajadores"])

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TrabajadorResponse)
def crear_trabajador(trabajador: TrabajadorCreate, db: Session = Depends(get_db)):
    return trabajador_servicio.crear_trabajador(db, trabajador)

@router.get("/", response_model=list[TrabajadorResponse])
def listar_trabajadores(db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores(db)

@router.get("/{trabajador_id}", response_model=TrabajadorResponse)
def obtener_trabajador(trabajador_id: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajador_por_id(db, trabajador_id)
