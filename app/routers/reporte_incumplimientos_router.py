# app/rutas/reporte_incumplimientos_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_db
from app.esquemas.reporte_incumplimientos_esquema import IncumplimientoResponse
from app.servicios.reporte_incumplimientos_servicio import obtener_incumplimientos_por_supervisor, obtener_incumplimientos_trabajador

router = APIRouter(prefix="/reportes/incumplimientos", tags=["Reportes - Incumplimientos"])


@router.get("/", response_model=list[IncumplimientoResponse])
def listar_incumplimientos(
    id_supervisor: int,
    db: Session = Depends(get_db)
):

    resultados = obtener_incumplimientos_por_supervisor(db, id_supervisor)

    return resultados

@router.get("/trabajador", response_model=list[IncumplimientoResponse])
def historial_trabajador(
    cedula: str | None = None,
    codigo_trabajador: str | None = None,
    id_trabajador: int | None = None,
    db: Session = Depends(get_db)
):
    return obtener_incumplimientos_trabajador(
        db,
        cedula,
        codigo_trabajador,
        id_trabajador
    )