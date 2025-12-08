from sqlalchemy.orm import Session
from app.modelos.evidencias_fallo import EvidenciaFallo  # ← clase correcta
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate
from datetime import datetime
import base64

def guardar_evidencia_fallo(db: Session, evidencia: EvidenciaFalloCreate):
    foto_bytes = base64.b64decode(evidencia.foto_base64)

    nuevo = EvidenciaFallo(
        foto_data=foto_bytes,
        detalle_fallo = evidencia.detalle_fallo,
        id_registro = evidencia.id_registro,
        fecha_captura = datetime.now(),
        borrado = True  # ✅ evitar borrado lógico accidental
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
