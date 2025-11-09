from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.inspector_zona_esquema import InspectorZonaCreate, InspectorZonaResponse
from app.servicios import inspector_zona_servicio

router = APIRouter(prefix="/inspector_zonas", tags=["Inspector - Zonas"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=InspectorZonaResponse)
def crear_inspector_zona(asignacion: InspectorZonaCreate, db: Session = Depends(get_db)):
    return inspector_zona_servicio.crear_inspector_zona(db, asignacion)

@router.get("/", response_model=list[InspectorZonaResponse])
def listar_inspector_zonas(db: Session = Depends(get_db)):
    return inspector_zona_servicio.obtener_inspector_zonas(db)

@router.get("/{asignacion_id}", response_model=InspectorZonaResponse)
def obtener_inspector_zona(asignacion_id: int, db: Session = Depends(get_db)):
    return inspector_zona_servicio.obtener_inspector_zona_por_id(db, asignacion_id)
