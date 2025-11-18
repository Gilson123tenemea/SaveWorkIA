from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import SessionLocal

from app.servicios.trabajador_zona_servicio import (
    crear_trabajador_zona,
    obtener_trabajador_zonas,
    obtener_trabajador_zona_por_id,
    eliminar_fisico_trabajador_zona,
    eliminar_logico_trabajador_zona,
    obtener_zonas_con_detalles_por_supervisor
)

from app.esquemas.trabajador_zona_esquema import (
    TrabajadorZonaCreate,
    TrabajadorZonaResponse
)
from app.esquemas.trabajador_zona_esquema import ZonaDetallesResponse
from app.esquemas.trabajador_zona_esquema import TrabajadorZonaDetalle
from app.servicios.trabajador_zona_servicio import obtener_trabajador_zonas_detalles

router = APIRouter(prefix="/trabajador_zonas", tags=["Trabajador - Zonas"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/supervisor/{id_supervisor}", response_model=list[ZonaDetallesResponse])
def listar_zonas_por_supervisor(id_supervisor: int, db: Session = Depends(get_db)):
    return obtener_zonas_con_detalles_por_supervisor(db, id_supervisor)

# =====================================================
# 🔥 IMPORTANTE: RUTA DETALLES DEBE IR ANTES DE /{id}
# =====================================================
@router.get("/detalles", response_model=list[TrabajadorZonaDetalle])
def listar_detalles(db: Session = Depends(get_db)):
    return obtener_trabajador_zonas_detalles(db)

# ===========================
# 📌 CRUD
# ===========================

@router.post("/", response_model=TrabajadorZonaResponse)
def crear(asignacion: TrabajadorZonaCreate, db: Session = Depends(get_db)):
    return crear_trabajador_zona(db, asignacion)


@router.get("/", response_model=list[TrabajadorZonaResponse])
def listar(db: Session = Depends(get_db)):
    return obtener_trabajador_zonas(db)


@router.get("/{asignacion_id}", response_model=TrabajadorZonaResponse)
def obtener(asignacion_id: int, db: Session = Depends(get_db)):
    asignacion = obtener_trabajador_zona_por_id(db, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return asignacion


@router.delete("/{asignacion_id}")
def eliminar_fisico(asignacion_id: int, db: Session = Depends(get_db)):
    ok = eliminar_fisico_trabajador_zona(db, asignacion_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return {"mensaje": "Asignación eliminada físicamente"}


@router.put("/eliminar-logico/{asignacion_id}", response_model=TrabajadorZonaResponse)
def eliminar_logico(asignacion_id: int, db: Session = Depends(get_db)):
    asignacion = eliminar_logico_trabajador_zona(db, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return asignacion

