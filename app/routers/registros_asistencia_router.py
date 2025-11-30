from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios.registros_asistencia_servicio import crear_registro_asistencia
from app.esquemas.registros_asistencia_esquema import RegistroAsistenciaCreate, RegistroAsistenciaResponse

router = APIRouter(prefix="/registros-asistencia", tags=["Registros de Asistencia"])


@router.post("/registrar", response_model=RegistroAsistenciaResponse)
def registrar_asistencia(asistencia: RegistroAsistenciaCreate, db: Session = Depends(get_db)):
    try:
        return crear_registro_asistencia(db, asistencia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar asistencia: {str(e)}")
