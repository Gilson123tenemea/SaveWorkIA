from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.config import get_db
from app.modelos.trabajador import Trabajador
from app.modelos.trabajador_zona import TrabajadorZona
from app.modelos.camara_modelo import Camara
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.zona_modelo import Zona

router = APIRouter(
    prefix="/dashboard-inspector",
    tags=["Dashboard Inspector"]
)


@router.get("/{id_zona}")
def obtener_dashboard_inspector(id_zona: int, db: Session = Depends(get_db)):

    # 1️⃣ Validar zona
    zona = db.query(Zona).filter(
        Zona.id_Zona == id_zona,
        Zona.borrado == True
    ).first()

    if not zona:
        raise HTTPException(status_code=404, detail="❌ Zona no encontrada")

    # 2️⃣ Trabajadores asignados a la zona (tabla intermedia)
    trabajadores = (
        db.query(TrabajadorZona)
        .filter(
            TrabajadorZona.id_zona_trabajadorzona == id_zona,
            TrabajadorZona.borrado == True
        )
        .count()
    )

    # 3️⃣ Cámaras de la zona
    camaras_ids = [
        c.id_camara
        for c in db.query(Camara).filter(
            Camara.id_zona == id_zona,
            Camara.borrado == True
        ).all()
    ]

    # Si no hay cámaras, no hay alertas
    if not camaras_ids:
        return {
            "zona": {
                "id_zona": zona.id_Zona,
                "nombre": zona.nombreZona
            },
            "alertas_hoy": 0,
            "alertas_mes": 0,
            "trabajadores": trabajadores,
            "incumplimientos_alta": 0
        }

    # 4️⃣ Registros de asistencia de esas cámaras
    registros_ids = [
        r.id_registro
        for r in db.query(RegistroAsistencia).filter(
            RegistroAsistencia.id_camara.in_(camaras_ids)
        ).all()
    ]

    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    # 🔴 Alertas HOY
    alertas_hoy = db.query(EvidenciaFallo).filter(
        EvidenciaFallo.id_registro.in_(registros_ids),
        EvidenciaFallo.borrado == True,
        EvidenciaFallo.fecha_captura >= datetime.combine(hoy, datetime.min.time()),
        EvidenciaFallo.fecha_captura <= datetime.combine(hoy, datetime.max.time())
    ).count()

    # 🟠 Alertas del MES
    alertas_mes = db.query(EvidenciaFallo).filter(
        EvidenciaFallo.id_registro.in_(registros_ids),
        EvidenciaFallo.borrado == True,
        EvidenciaFallo.fecha_captura >= inicio_mes
    ).count()

    # 🔥 Incumplimientos ALTA prioridad (pendientes)
    incumplimientos_alta = db.query(EvidenciaFallo).filter(
        EvidenciaFallo.id_registro.in_(registros_ids),
        EvidenciaFallo.borrado == True,
        EvidenciaFallo.estado == 0
    ).count()

    return {
        "zona": {
            "id_zona": zona.id_Zona,
            "nombre": zona.nombreZona
        },
        "alertas_hoy": alertas_hoy,
        "alertas_mes": alertas_mes,
        "trabajadores": trabajadores,
        "incumplimientos_alta": incumplimientos_alta
    }
