from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.trabajador_zona_esquema import TrabajadorZonaCreate, TrabajadorZonaResponse
from app.servicios import trabajador_zona_servicio

router = APIRouter(prefix="/trabajador_zonas", tags=["Trabajador - Zonas"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TrabajadorZonaResponse)
def crear_trabajador_zona(asignacion: TrabajadorZonaCreate, db: Session = Depends(get_db)):
    return trabajador_zona_servicio.crear_trabajador_zona(db, asignacion)

@router.get("/", response_model=list[TrabajadorZonaResponse])
def listar_trabajador_zonas(db: Session = Depends(get_db)):
    return trabajador_zona_servicio.obtener_trabajador_zonas(db)

@router.get("/{asignacion_id}", response_model=TrabajadorZonaResponse)
def obtener_trabajador_zona(asignacion_id: int, db: Session = Depends(get_db)):
    return trabajador_zona_servicio.obtener_trabajador_zona_por_id(db, asignacion_id)
