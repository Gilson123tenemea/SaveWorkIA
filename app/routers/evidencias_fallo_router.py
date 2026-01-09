from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios.evidencias_fallo_servicio import guardar_evidencia_fallo, actualizar_evidencia_fallo
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate, EvidenciaFalloResponse, EvidenciaFalloUpdate
from app.servicios.notificaciones_fcm_servicio import NotificacionesFCMServicio
from app.modelos.inspector_zona import InspectorZona

router = APIRouter(prefix="/evidencias-fallo", tags=["Evidencias de Fallo EPP"])


@router.post("/guardar", response_model=EvidenciaFalloResponse)
def guardar_evidencia(evidencia: EvidenciaFalloCreate, db: Session = Depends(get_db)):
    """
    Guarda una nueva evidencia de fallo EPP.
    
    El servicio guardar_evidencia_fallo ya maneja:
    - Guardado en BD
    - Búsqueda del inspector
    - Envío de notificación push
    """
    try:
        # El servicio ahora maneja todo (guardado + notificación)
        evidencia_guardada = guardar_evidencia_fallo(db, evidencia)
        return evidencia_guardada
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en ruta al guardar evidencia: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al guardar evidencia: {str(e)}"
        )


@router.put("/actualizar/{id_evidencia}")
def actualizar_evidencia(
    id_evidencia: int, 
    cambios: EvidenciaFalloUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualiza una evidencia de fallo existente.
    
    Nota: No envía notificación al actualizar, solo al crear.
    """
    try:
        evidencia = actualizar_evidencia_fallo(db, id_evidencia, cambios)
        
        if not evidencia:
            raise HTTPException(
                status_code=404, 
                detail="❌ Evidencia no encontrada"
            )

        print(f"✅ Evidencia {id_evidencia} actualizada correctamente")
        return evidencia

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al actualizar evidencia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error al actualizar evidencia: {str(e)}"
        )