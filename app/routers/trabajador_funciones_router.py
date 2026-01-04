from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import get_db
from app.esquemas.trabajador_funciones_esquema import TrabajadorEstadisticasResponse
from app.servicios.trabajador_funciones_servicio import obtener_estadisticas_trabajador
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.esquemas.trabajador_funciones_esquema import (
    TrabajadorLoginRequest,
    TrabajadorLoginResponse,
    TrabajadorPerfilResponse,
    IncumplimientosTrabajadorResponse,
    TrabajadorEstadisticasResponse,
    HistorialAsistenciasResponse
)
from app.servicios.trabajador_funciones_servicio import (
    login_trabajador,
    obtener_perfil_trabajador,
    obtener_incumplimientos_por_trabajador,
    obtener_estadisticas_trabajador,
    obtener_historial_asistencias
)


router = APIRouter(prefix="/trabajadores", tags=["Trabajador - Funciones"])


@router.post("/login", response_model=TrabajadorLoginResponse)
def login(request: TrabajadorLoginRequest, db: Session = Depends(get_db)):
    return login_trabajador(db, request.correo, request.contrasena)


@router.get("/{id_trabajador}/perfil", response_model=TrabajadorPerfilResponse)
def perfil_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    return obtener_perfil_trabajador(db, id_trabajador)

@router.get(
    "/{id_trabajador}/estadisticas",
    response_model=TrabajadorEstadisticasResponse
)
def estadisticas_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    return obtener_estadisticas_trabajador(db, id_trabajador)

@router.get(
    "/{id_trabajador}/incumplimientos",
    response_model=IncumplimientosTrabajadorResponse
)
def historial_incumplimientos_trabajador(
    id_trabajador: int,
    db: Session = Depends(get_db)
):
    return obtener_incumplimientos_por_trabajador(db, id_trabajador)

@router.get(
    "/{id_trabajador}/asistencias",
    response_model=HistorialAsistenciasResponse
)
def historial_asistencias(
    id_trabajador: int,
    mes: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    año: Optional[int] = Query(None, ge=2000, description="Año (ej: 2024)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de asistencias registradas del trabajador.
    
    Parámetros:
    - id_trabajador: ID del trabajador
    - mes: (Opcional) Mes para filtrar (1-12)
    - año: (Opcional) Año para filtrar
    
    Muestra: fecha, hora, código trabajador, cédula, nombre, apellido, 
    zona, inspector, cámara y si cumple o no con EPP
    
    Ejemplos de uso:
    - GET /trabajadores/1/asistencias → Todo el historial
    - GET /trabajadores/1/asistencias?año=2024 → Solo 2024
    - GET /trabajadores/1/asistencias?mes=3&año=2024 → Marzo 2024
    """
    return obtener_historial_asistencias(db, id_trabajador, mes, año)