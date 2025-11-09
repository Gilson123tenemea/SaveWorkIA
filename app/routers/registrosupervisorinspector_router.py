from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.registrosupervisorinspector_esquema import (
    RegistroSupervisorInspectorCreate,
    RegistroSupervisorInspectorResponse,
)
from app.servicios import registrosupervisorinspector_servicio

router = APIRouter(
    prefix="/registros_supervisor_inspector",
    tags=["Registro Supervisor - Inspector"]
)

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=RegistroSupervisorInspectorResponse)
def crear_registro(registro: RegistroSupervisorInspectorCreate, db: Session = Depends(get_db)):
    return registrosupervisorinspector_servicio.crear_registro(db, registro)

@router.get("/", response_model=list[RegistroSupervisorInspectorResponse])
def listar_registros(db: Session = Depends(get_db)):
    return registrosupervisorinspector_servicio.obtener_registros(db)

@router.get("/{registro_id}", response_model=RegistroSupervisorInspectorResponse)
def obtener_registro(registro_id: int, db: Session = Depends(get_db)):
    return registrosupervisorinspector_servicio.obtener_registro_por_id(db, registro_id)
