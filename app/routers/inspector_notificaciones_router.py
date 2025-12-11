from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.config import get_db

from app.modelos.inspector_zona import InspectorZona
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.registros_asistencia import RegistroAsistencia

router = APIRouter(prefix="/inspectores", tags=["Inspector Notificaciones"])

@router.get("/{id_inspector}/notificaciones")
def obtener_notificaciones_inspector(id_inspector: int, db: Session = Depends(get_db)):

    zona = (
        db.query(InspectorZona)
        .filter(
            InspectorZona.id_inspector_inspectorzona == id_inspector,
            InspectorZona.borrado == True
        )
        .first()
    )

    if not zona:
        return []

    id_zona = zona.id_zona_inspectorzona

    evidencias = (
        db.query(EvidenciaFallo)
        .join(RegistroAsistencia, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .filter(
            EvidenciaFallo.borrado == True,
            RegistroAsistencia.id_zona == id_zona,
            or_(EvidenciaFallo.estado == True, EvidenciaFallo.estado == None)
        )
        .order_by(EvidenciaFallo.fecha_captura.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "id": ev.id_evidencia,
            "detalle": ev.detalle_fallo,
            "fecha": ev.fecha_captura,
            "estado": ev.estado,
            "zona": ev.registro.zona.nombreZona,
            "trabajador": f"{ev.registro.trabajador.persona.nombre} {ev.registro.trabajador.persona.apellido}"
        }
        for ev in evidencias
    ]

@router.put("/notificaciones/{id_evidencia}/revisar")
def marcar_notificacion_revisada(id_evidencia: int, db: Session = Depends(get_db)):

    evidencia = db.query(EvidenciaFallo).filter(
        EvidenciaFallo.id_evidencia == id_evidencia
    ).first()

    if not evidencia:
        return {"error": "Evidencia no encontrada"}

    evidencia.estado = False   # 🔥 pasa de pendiente (true/1) a revisado
    db.commit()
    return {"mensaje": "Notificación marcada como revisada"}
