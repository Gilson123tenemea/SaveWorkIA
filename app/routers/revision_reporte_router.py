# app/routers/revision_reporte_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.revision_reporte_esquema import RevisionReporteCreate, RevisionReporteResponse, RevisionReporteUpdate
from app.servicios import revision_reporte_servicio
from datetime import date

router = APIRouter(prefix="/revisiones-reportes", tags=["Revisiones de Reportes"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=RevisionReporteResponse, status_code=201)
def crear_revision(revision: RevisionReporteCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva revisión de reporte en el sistema
    """
    return revision_reporte_servicio.crear_revision(db, revision)

@router.get("/", response_model=list[RevisionReporteResponse])
def listar_revisiones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las revisiones activas (no eliminadas)
    """
    return revision_reporte_servicio.obtener_revisiones(db, skip, limit)

@router.get("/supervisor/{supervisor_id}", response_model=list[RevisionReporteResponse])
def listar_revisiones_por_supervisor(
    supervisor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las revisiones realizadas por un supervisor específico
    """
    return revision_reporte_servicio.obtener_revisiones_por_supervisor(db, supervisor_id, skip, limit)

@router.get("/reporte/{reporte_id}", response_model=list[RevisionReporteResponse])
def listar_revisiones_por_reporte(
    reporte_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las revisiones de un reporte específico
    """
    return revision_reporte_servicio.obtener_revisiones_por_reporte(db, reporte_id, skip, limit)

@router.get("/reporte/{reporte_id}/ultima", response_model=RevisionReporteResponse)
def obtener_ultima_revision_reporte(reporte_id: int, db: Session = Depends(get_db)):
    """
    Obtiene la última revisión realizada a un reporte
    """
    return revision_reporte_servicio.obtener_ultima_revision_reporte(db, reporte_id)

@router.get("/fecha-rango", response_model=list[RevisionReporteResponse])
def listar_revisiones_por_fecha(
    fecha_inicio: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las revisiones entre dos fechas
    """
    return revision_reporte_servicio.obtener_revisiones_por_fecha(db, fecha_inicio, fecha_fin, skip, limit)

@router.get("/{revision_id}", response_model=RevisionReporteResponse)
def obtener_revision(revision_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una revisión específica por su ID
    """
    return revision_reporte_servicio.obtener_revision_por_id(db, revision_id)

@router.get("/estadisticas/supervisor/{supervisor_id}")
def contar_revisiones_supervisor(supervisor_id: int, db: Session = Depends(get_db)):
    """
    Cuenta el total de revisiones realizadas por un supervisor
    """
    return revision_reporte_servicio.contar_revisiones_por_supervisor(db, supervisor_id)

@router.get("/estadisticas/reporte/{reporte_id}")
def contar_revisiones_reporte(reporte_id: int, db: Session = Depends(get_db)):
    """
    Cuenta el total de revisiones de un reporte
    """
    return revision_reporte_servicio.contar_revisiones_por_reporte(db, reporte_id)

@router.put("/{revision_id}", response_model=RevisionReporteResponse)
def actualizar_revision(
    revision_id: int,
    revision_update: RevisionReporteUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de una revisión
    """
    return revision_reporte_servicio.actualizar_revision(db, revision_id, revision_update)

@router.delete("/{revision_id}")
def eliminar_revision(revision_id: int, db: Session = Depends(get_db)):
    """
    Elimina lógicamente una revisión (marca como borrado)
    """
    return revision_reporte_servicio.eliminar_revision(db, revision_id)

@router.delete("/{revision_id}/permanente")
def eliminar_revision_permanente(revision_id: int, db: Session = Depends(get_db)):
    """
    Elimina físicamente una revisión de la base de datos
    ⚠️ Esta acción es irreversible
    """
    return revision_reporte_servicio.eliminar_revision_permanente(db, revision_id)