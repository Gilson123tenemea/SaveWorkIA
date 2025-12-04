# app/rutas/reporte_incumplimientos_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_db
from app.esquemas.reporte_incumplimientos_esquema import IncumplimientoResponse
from app.servicios.reporte_incumplimientos_servicio import obtener_incumplimientos_por_supervisor

router = APIRouter(prefix="/reportes/incumplimientos", tags=["Reportes - Incumplimientos"])


@router.get("/", response_model=list[IncumplimientoResponse])
def listar_incumplimientos(
    id_supervisor: int,
    db: Session = Depends(get_db)
):

    resultados = obtener_incumplimientos_por_supervisor(db, id_supervisor)

    return resultados
