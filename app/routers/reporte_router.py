from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.reporte_esquema import ReporteCreate, ReporteResponse
from app.servicios import reporte_servicio

router = APIRouter(prefix="/reportes", tags=["Reportes"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ReporteResponse)
def crear_reporte(reporte: ReporteCreate, db: Session = Depends(get_db)):
    return reporte_servicio.crear_reporte(db, reporte)

@router.get("/", response_model=list[ReporteResponse])
def listar_reportes(db: Session = Depends(get_db)):
    return reporte_servicio.obtener_reportes(db)

@router.get("/{reporte_id}", response_model=ReporteResponse)
def obtener_reporte(reporte_id: int, db: Session = Depends(get_db)):
    return reporte_servicio.obtener_reporte_por_id(db, reporte_id)
