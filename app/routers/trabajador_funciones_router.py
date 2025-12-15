from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import get_db
from app.esquemas.trabajador_funciones_esquema import TrabajadorEstadisticasResponse
from app.servicios.trabajador_funciones_servicio import obtener_estadisticas_trabajador

from app.esquemas.trabajador_funciones_esquema import (
    TrabajadorLoginRequest,
    TrabajadorLoginResponse,
    TrabajadorPerfilResponse,
    IncumplimientosTrabajadorResponse
)
from app.servicios.trabajador_funciones_servicio import (
    login_trabajador,
    obtener_perfil_trabajador,
    obtener_incumplimientos_por_trabajador
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