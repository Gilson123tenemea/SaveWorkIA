from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.config import get_db
from app.modelos.trabajador_zona import TrabajadorZona
from app.modelos.camara_modelo import Camara
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.zona_modelo import Zona
from app.modelos.inspector_zona import InspectorZona

router = APIRouter(
    prefix="/dashboard-inspector",
    tags=["Dashboard Inspector"]
)


@router.get("/{id_inspector}")
def obtener_dashboard_inspector(id_inspector: int, db: Session = Depends(get_db)):

    # 1️⃣ ZONAS asignadas al inspector
    zonas_ids = [
        iz.id_zona_inspectorzona
        for iz in db.query(InspectorZona).filter(
            InspectorZona.id_inspector_inspectorzona == id_inspector,
            InspectorZona.borrado == True
        ).all()
    ]

    if not zonas_ids:
        raise HTTPException(
            status_code=404,
            detail="❌ El inspector no tiene zonas asignadas"
        )

    # 2️⃣ TRABAJADORES (todas las zonas)
    trabajadores = db.query(TrabajadorZona).filter(
        TrabajadorZona.id_zona_trabajadorzona.in_(zonas_ids),
        TrabajadorZona.borrado == True
    ).count()

    # 3️⃣ CÁMARAS (todas las zonas)
    camaras = db.query(Camara).filter(
        Camara.id_zona.in_(zonas_ids),
        Camara.borrado == True
    ).all()

    camaras_ids = [c.id_camara for c in camaras]

    camaras_totales = len(camaras)
    camaras_activas = len([c for c in camaras if c.estado == True])

    # Si no hay cámaras → no hay alertas
    if not camaras_ids:
        return {
            "zonas_asignadas": len(zonas_ids),
            "trabajadores": trabajadores,
            "alertas_hoy": 0,
            "alertas_mes": 0,
            "incumplimientos_alta": 0,
            "camaras_totales": camaras_totales,
            "camaras_activas": camaras_activas
        }

    # 4️⃣ REGISTROS de asistencia
    registros_ids = [
        r.id_registro
        for r in db.query(RegistroAsistencia).filter(
            RegistroAsistencia.id_camara.in_(camaras_ids)
        ).all()
    ]

    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    # 🔴 ALERTAS HOY
    alertas_hoy = db.query(EvidenciaFallo).filter(
        EvidenciaFallo.id_registro.in_(registros_ids),
        EvidenciaFallo.borrado == True,
        EvidenciaFallo.fecha_captura >= datetime.combine(hoy, datetime.min.time()),
        EvidenciaFallo.fecha_captura <= datetime.combine(hoy, datetime.max.time())
    ).count()

    # 🟠 ALERTAS DEL MES
    alertas_mes = db.query(EvidenciaFallo).filter(
        EvidenciaFallo.id_registro.in_(registros_ids),
        EvidenciaFallo.borrado == True,
        EvidenciaFallo.fecha_captura >= inicio_mes
    ).count()

    # 🔥 INCUMPLIMIENTOS ALTA PRIORIDAD (pendientes)
    incumplimientos_alta = db.query(EvidenciaFallo).filter(
        EvidenciaFallo.id_registro.in_(registros_ids),
        EvidenciaFallo.borrado == True,
        EvidenciaFallo.estado == 0
    ).count()

    return {
        "zonas_asignadas": len(zonas_ids),
        "trabajadores": trabajadores,
        "alertas_hoy": alertas_hoy,
        "alertas_mes": alertas_mes,
        "incumplimientos_alta": incumplimientos_alta,
        "camaras_totales": camaras_totales,
        "camaras_activas": camaras_activas
    }