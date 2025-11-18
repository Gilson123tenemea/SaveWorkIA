from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import SessionLocal
from app.esquemas.inspector_zona_esquema import (
    InspectorZonaCreate,
    InspectorZonaResponse,
    InspectorZonaFullResponse
)
from app.servicios import inspector_zona_servicio

router = APIRouter(prefix="/inspector_zonas", tags=["Inspector - Zonas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=InspectorZonaResponse)
def crear(asignacion: InspectorZonaCreate, db: Session = Depends(get_db)):
    return inspector_zona_servicio.crear_inspector_zona(db, asignacion)


@router.get("/", response_model=list[InspectorZonaResponse])
def listar(db: Session = Depends(get_db)):
    return inspector_zona_servicio.obtener_inspector_zonas(db)


@router.get("/{asignacion_id}", response_model=InspectorZonaResponse)
def obtener(asignacion_id: int, db: Session = Depends(get_db)):
    asignacion = inspector_zona_servicio.obtener_inspector_zona_por_id(db, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return asignacion


@router.put("/{asignacion_id}", response_model=InspectorZonaResponse)
def actualizar(asignacion_id: int, data: InspectorZonaCreate, db: Session = Depends(get_db)):
    asignacion = inspector_zona_servicio.actualizar_inspector_zona(db, asignacion_id, data)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return asignacion


@router.delete("/{asignacion_id}", response_model=InspectorZonaResponse)
def eliminar(asignacion_id: int, db: Session = Depends(get_db)):
    asignacion = inspector_zona_servicio.eliminar_inspector_zona(db, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return asignacion

@router.get("/empresa/{empresa_id}")
def listar_por_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return inspector_zona_servicio.obtener_asignaciones_completas(db, empresa_id)
