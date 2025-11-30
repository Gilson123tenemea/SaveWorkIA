from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios.evidencias_fallo_servicio import guardar_evidencia_fallo
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate, EvidenciaFalloResponse

router = APIRouter(prefix="/evidencias-fallo", tags=["Evidencias de Fallo EPP"])


@router.post("/guardar", response_model=EvidenciaFalloResponse)
def guardar_evidencia(evidencia: EvidenciaFalloCreate, db: Session = Depends(get_db)):
    try:
        return guardar_evidencia_fallo(db, evidencia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar evidencia: {str(e)}")
