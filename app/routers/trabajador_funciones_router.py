from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.config import get_db
from app.esquemas.trabajador_funciones_esquema import (
    TrabajadorLoginRequest,
    TrabajadorLoginResponse,
    TrabajadorPerfilResponse,
    IncumplimientosTrabajadorResponse,
    TrabajadorEstadisticasResponse,
    HistorialAsistenciasResponse,
    ActualizarTrabajadorResponse
)
from app.servicios.trabajador_funciones_servicio import (
    login_trabajador,
    obtener_perfil_trabajador,
    obtener_incumplimientos_por_trabajador,
    obtener_estadisticas_trabajador,
    obtener_historial_asistencias,
    actualizar_trabajador
)


router = APIRouter(prefix="/trabajadores", tags=["Trabajador - Funciones"])


@router.post("/login", response_model=TrabajadorLoginResponse)
def login(request: TrabajadorLoginRequest, db: Session = Depends(get_db)):
    """Login de trabajador con correo y contraseña"""
    return login_trabajador(db, request.correo, request.contrasena)


@router.get("/{id_trabajador}/perfil", response_model=TrabajadorPerfilResponse)
def perfil_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    """Obtiene el perfil completo del trabajador"""
    return obtener_perfil_trabajador(db, id_trabajador)


@router.get(
    "/{id_trabajador}/estadisticas",
    response_model=TrabajadorEstadisticasResponse
)
def estadisticas_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    """Obtiene las estadísticas generales del trabajador"""
    return obtener_estadisticas_trabajador(db, id_trabajador)


@router.get(
    "/{id_trabajador}/incumplimientos",
    response_model=IncumplimientosTrabajadorResponse
)
def historial_incumplimientos_trabajador(
    id_trabajador: int,
    db: Session = Depends(get_db)
):
    """Obtiene el historial detallado de incumplimientos del trabajador"""
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
    """Obtiene el historial de asistencias registradas del trabajador"""
    return obtener_historial_asistencias(db, id_trabajador, mes, año)


@router.patch("/{id_trabajador}", response_model=ActualizarTrabajadorResponse)
def actualizar_datos_trabajador(
    id_trabajador: int,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos del trabajador.
    
    Campos editables:
    - nombre: Nombre del trabajador
    - apellido: Apellido del trabajador
    - correo: Correo electrónico (debe ser único)
    - telefono: Número de teléfono (10 dígitos)
    - cargo: Cargo/puesto del trabajador
    
    Envía los datos así:
    {
        "nombre": "Juan",
        "apellido": "Pérez",
        "correo": "juan.perez@example.com",
        "telefono": "0987654321",
        "cargo": "Técnico"
    }
    """
    return actualizar_trabajador(
        db,
        id_trabajador,
        nombre=payload.get("nombre"),
        apellido=payload.get("apellido"),
        correo=payload.get("correo"),
        telefono=payload.get("telefono"),
        cargo=payload.get("cargo")
    )