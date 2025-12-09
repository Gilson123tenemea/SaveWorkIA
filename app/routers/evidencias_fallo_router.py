from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios.evidencias_fallo_servicio import guardar_evidencia_fallo, actualizar_evidencia_fallo
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate, EvidenciaFalloResponse, EvidenciaFalloUpdate

router = APIRouter(prefix="/evidencias-fallo", tags=["Evidencias de Fallo EPP"])


@router.post("/guardar", response_model=EvidenciaFalloResponse)
def guardar_evidencia(evidencia: EvidenciaFalloCreate, db: Session = Depends(get_db)):
    try:
        return guardar_evidencia_fallo(db, evidencia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar evidencia: {str(e)}")

@router.put("/actualizar/{id_evidencia}")
def actualizar_evidencia(id_evidencia: int, cambios: EvidenciaFalloUpdate, db: Session = Depends(get_db)):
    try:
        evidencia = actualizar_evidencia_fallo(db, id_evidencia, cambios)
        if not evidencia:
            raise HTTPException(404, "❌ Evidencia no encontrada")

        return evidencia

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error al actualizar evidencia: {str(e)}"
        )