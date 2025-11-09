from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.inspector_reporte_esquema import (
    InspectorReporteCreate,
    InspectorReporteResponse,
)
from app.servicios import inspector_reporte_servicio

router = APIRouter(prefix="/inspector_reportes", tags=["Inspector - Reportes"])

# Dependencia para la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=InspectorReporteResponse)
def crear_inspector_reporte(registro: InspectorReporteCreate, db: Session = Depends(get_db)):
    return inspector_reporte_servicio.crear_inspector_reporte(db, registro)

@router.get("/", response_model=list[InspectorReporteResponse])
def listar_inspector_reportes(db: Session = Depends(get_db)):
    return inspector_reporte_servicio.obtener_inspector_reportes(db)

@router.get("/{registro_id}", response_model=InspectorReporteResponse)
def obtener_inspector_reporte(registro_id: int, db: Session = Depends(get_db)):
    return inspector_reporte_servicio.obtener_inspector_reporte_por_id(db, registro_id)
