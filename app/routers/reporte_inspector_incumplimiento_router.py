# app/rutas/reporte_inspector_incumplimiento_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_db
from app.esquemas.reporte_inspector_incumplimiento_esquema import (
    IncumplimientoInspectorResponse,
    HistorialIncumplimientoInspectorResponse
)
from app.servicios.reporte_inspector_incumplimiento_servicio import obtener_incumplimientos_por_inspector, obtener_incumplimientos_por_cedula, obtener_zonas_por_inspector

router = APIRouter(
    prefix="/reportes/inspectores",
    tags=["Reportes - Inspector"]
)


@router.get("/", response_model=list[IncumplimientoInspectorResponse])
def listar_incumplimientos_inspector(
    id_inspector: int,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    id_zona: int | None = None,
    db: Session = Depends(get_db)
):
    return obtener_incumplimientos_por_inspector(
        db=db,
        id_inspector=id_inspector,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        id_zona=id_zona
    )

@router.get(
    "/trabajador",
    response_model=HistorialIncumplimientoInspectorResponse
)
def historial_por_cedula(
    cedula: str,
    db: Session = Depends(get_db)
):
    return obtener_incumplimientos_por_cedula(db, cedula)



@router.get("/zonas")
def listar_zonas_inspector(
    id_inspector: int,
    db: Session = Depends(get_db)
):
    return obtener_zonas_por_inspector(db, id_inspector)
