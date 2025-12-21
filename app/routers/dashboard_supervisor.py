from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.modelos.trabajador import Trabajador
from app.modelos.camara_modelo import Camara
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.zona_modelo import Zona
from app.modelos.empresa_modelo import Empresa

router = APIRouter(prefix="/dashboard-supervisor", tags=["Dashboard Supervisor"])


@router.get("/{id_empresa}")
def obtener_dashboard_supervisor(id_empresa: int, db: Session = Depends(get_db)):

    trabajadores_activos = db.query(Trabajador).filter(
        Trabajador.id_empresa == id_empresa,
        Trabajador.borrado == True,
        Trabajador.estado == True
    ).count()

    trabajadores_registrados = db.query(Trabajador).filter(
        Trabajador.id_empresa == id_empresa,
        Trabajador.borrado == True
    ).count()

    # Zonas de la empresa
    zonas = db.query(Zona).filter(
        Zona.id_empresa_zona == id_empresa,
        Zona.borrado == True
    ).all()

    # Cámaras activas y totales
    camaras_totales = 0
    camaras_activas = 0

    for zona in zonas:
        camaras_totales += len(zona.camaras)
        camaras_activas += len([c for c in zona.camaras if c.estado == "activa"])

    # Alertas activas de evidencias de fallos
    alertas_activas = db.query(EvidenciaFallo).join(RegistroAsistencia).filter(
        RegistroAsistencia.id_empresa == id_empresa,
        EvidenciaFallo.borrado == True
    ).count()

    # Cumplimiento EPP
    epp_completo = db.query(RegistroAsistencia).filter(
        RegistroAsistencia.id_empresa == id_empresa,
        RegistroAsistencia.cumple_epp == True
    ).count()

    porcentaje_epp = 0
    if trabajadores_registrados > 0:
        porcentaje_epp = round((epp_completo / trabajadores_registrados) * 100, 2)

    return {
        "trabajadores_activos": trabajadores_activos,
        "trabajadores_registrados": trabajadores_registrados,
        "epp_completo": epp_completo,
        "porcentaje_epp": porcentaje_epp,
        "alertas_activas": alertas_activas,
        "camaras_totales": camaras_totales,
        "camaras_activas": camaras_activas
    }