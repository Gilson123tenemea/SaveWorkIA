from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.inspector_esquema import InspectorCreate, InspectorResponse
from app.servicios import inspector_servicio

router = APIRouter(prefix="/inspectores", tags=["Inspectores"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=InspectorResponse)
def crear_inspector(inspector: InspectorCreate, db: Session = Depends(get_db)):
    return inspector_servicio.crear_inspector(db, inspector)

@router.get("/", response_model=list[InspectorResponse])
def listar_inspectores(db: Session = Depends(get_db)):
    return inspector_servicio.obtener_inspectores(db)

@router.get("/{inspector_id}", response_model=InspectorResponse)
def obtener_inspector(inspector_id: int, db: Session = Depends(get_db)):
    return inspector_servicio.obtener_inspector_por_id(db, inspector_id)
