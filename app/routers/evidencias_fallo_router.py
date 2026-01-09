
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios.evidencias_fallo_servicio import (
    guardar_evidencia_fallo,
    actualizar_evidencia_fallo
)
from app.esquemas.evidencias_fallo_esquema import (
    EvidenciaFalloCreate,
    EvidenciaFalloResponse,
    EvidenciaFalloUpdate
)

router = APIRouter(prefix="/evidencias-fallo", tags=["Evidencias de Fallo EPP"])


@router.post("/guardar", response_model=EvidenciaFalloResponse)
def guardar_evidencia(
    evidencia: EvidenciaFalloCreate,
    db: Session = Depends(get_db)
):
    """
    Guarda una nueva evidencia de fallo EPP.
    
    El proceso automático es:
    1. Guarda evidencia en BD
    2. Busca el inspector del registro
    3. Envía notificación push al inspector
    4. Retorna la evidencia guardada
    
    Si el inspector no tiene tokens registrados, la notificación se omite
    pero la evidencia se guarda correctamente.
    """
    try:
        print(f'\n🚀 === NUEVA EVIDENCIA DE FALLO === 🚀')
        print(f'   Detalle: {evidencia.detalle_fallo}')
        print(f'   Registro: {evidencia.id_registro}')
        
        # El servicio ahora maneja: guardado + búsqueda de inspector + notificación
        evidencia_guardada = guardar_evidencia_fallo(db, evidencia)
        
        print(f'\n✅ PROCESO COMPLETADO EXITOSAMENTE\n')
        
        return evidencia_guardada
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en ruta al guardar evidencia: {str(e)}")
        import traceback
        traceback.print_exc()
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
    
    Puede cambiar:
    - estado: false (revisada)
    - observaciones: comentarios del inspector
    
    Nota: No envía notificación al actualizar, solo al crear.
    """
    try:
        print(f'\n🔄 === ACTUALIZANDO EVIDENCIA {id_evidencia} === 🔄')
        
        evidencia = actualizar_evidencia_fallo(db, id_evidencia, cambios)
        
        if not evidencia:
            raise HTTPException(
                status_code=404, 
                detail="❌ Evidencia no encontrada"
            )

        print(f'✅ Respuesta enviada')
        return evidencia

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al actualizar evidencia: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error al actualizar evidencia: {str(e)}"
        )