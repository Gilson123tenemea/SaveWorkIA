from sqlalchemy.orm import Session
from app.modelos.evidencias_fallo import EvidenciaFallo  # ← clase correcta
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate
from datetime import datetime

def guardar_evidencia_fallo(db: Session, evidencia: EvidenciaFalloCreate):
    nuevo = EvidenciaFallo(
        foto_url = evidencia.foto_url,
        detalle_fallo = evidencia.detalle_fallo,
        id_registro = evidencia.id_registro,
        fecha_captura = datetime.now(),
        borrado = True  # ✅ evitar borrado lógico accidental
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
