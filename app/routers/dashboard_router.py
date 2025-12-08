from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.config import get_db

from app.modelos.empresa_modelo import Empresa
from app.modelos.supervisor import Supervisor
from app.modelos.camara_modelo import Camara
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.registros_asistencia import RegistroAsistencia

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def tiempo_relativo(fecha):
    diff = datetime.now() - fecha
    if diff.seconds < 60:
        return "Hace un momento"
    elif diff.seconds < 3600:
        return f"Hace {diff.seconds // 60} min"
    elif diff.seconds < 86400:
        return f"Hace {diff.seconds // 3600} h"
    else:
        return f"Hace {diff.days} días"


@router.get("/overview")
def obtener_dashboard_overview(db: Session = Depends(get_db)):

    total_empresas = db.query(Empresa).filter(Empresa.borrado == True).count()
    usuarios_activos = db.query(Supervisor).filter(Supervisor.borrado == True).count()

    total_camaras = db.query(Camara).filter(Camara.borrado == True).count()
    camaras_activas = db.query(Camara).filter(
        Camara.borrado == True,
        Camara.estado == "activa"
    ).count()

    # 🔥 Cargar evidencias con join hacia Registro → Empresa
    evidencias = (
        db.query(EvidenciaFallo)
        .join(RegistroAsistencia, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .join(Empresa, RegistroAsistencia.id_empresa == Empresa.id_Empresa)
        .add_entity(RegistroAsistencia)
        .add_entity(Empresa)
        .filter(EvidenciaFallo.borrado == True)
        .order_by(EvidenciaFallo.fecha_captura.desc())
        .limit(10)
        .all()
    )

    alertas_recientes = []
    for evidencia, registro, empresa in evidencias:
        alertas_recientes.append({
            "id": evidencia.id_evidencia,
            "mensaje": evidencia.detalle_fallo,
            "tiempo": tiempo_relativo(evidencia.fecha_captura),
            "empresa": empresa.nombreEmpresa,     # 👈 NOMBRE DE LA EMPRESA
            "empresa_id": empresa.id_Empresa,
            "nivel": "high",                     # puedes mejorarlo luego
            "registro_id": registro.id_registro
        })

    hoy = datetime.now().date()
    alertas_hoy = (
        db.query(EvidenciaFallo)
        .filter(EvidenciaFallo.fecha_captura >= datetime.combine(hoy, datetime.min.time()))
        .count()
    )

    return {
        "total_empresas": total_empresas,
        "usuarios_activos": usuarios_activos,
        "camaras_totales": total_camaras,
        "camaras_activas": camaras_activas,
        "alertas_hoy": alertas_hoy,
        "alertas_recientes": alertas_recientes,
        "estado_sistema": {
            "servidor_ia": "online",
            "camaras": "online" if camaras_activas > 0 else "warning",
            "base_datos": "online",
            "almacenamiento": "online"
        }
    }
