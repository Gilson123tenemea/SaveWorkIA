from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios.registros_asistencia_servicio import crear_registro_asistencia
from app.servicios.evidencias_fallo_servicio import guardar_evidencia_fallo  # ✅ Import correcto
from app.esquemas.registros_asistencia_esquema import RegistroAsistenciaCreate, RegistroAsistenciaResponse
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate  # ✅ Esquema evidencia

router = APIRouter(prefix="/registros-asistencia", tags=["Registros de Asistencia"])

@router.post("/registrar", response_model=RegistroAsistenciaResponse)
def registrar_asistencia(asistencia: RegistroAsistenciaCreate, db: Session = Depends(get_db)):
    try:
        # 1. Crear asistencia normal
        registro = crear_registro_asistencia(db, asistencia)

        # 2. 🔥 Si no cumple EPP → Crear evidencia del fallo automáticamente
        if not registro.cumple_epp:  # FALSE = 0 en MySQL
            evidencia = EvidenciaFalloCreate(
                foto_url = "pendiente",  # luego desde IA actualizas la foto real
                detalle_fallo = asistencia.tipo_fallo if hasattr(asistencia, 'tipo_fallo') else "Incumplimiento EPP",
                id_registro = registro.id_registro,
            )
            guardar_evidencia_fallo(db, evidencia)

        return registro
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error al registrar asistencia: {str(e)}")
